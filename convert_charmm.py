import sys
import re
import networkx as nx
import numpy as np

"""
Este script está diseñado para facilitar la conversión de información de topología molecular desde archivos CHARMM a formatos compatibles con GROMACS. Para utilizar este script, siga los siguientes pasos:

Requisitos:
- Python 2.7.3 o una versión compatible.
- Archivo de topología RTP CHARMM (rtp_name).
- Archivo .mol2 de la molécula de interés (mol2_name).
- Directorio que contiene los archivos de fuerza CHARMM36 (ffdir).
- Archivo atomtypes.atp en el directorio de fuerza CHARMM36 (ffdir).

Pasos para usar el script:

1. Ejecute el script proporcionando los siguientes argumentos en la línea de comandos:
   - RESNAME: El nombre de la molécula de interés.
   - Ruta al archivo .mol2 de la molécula (drug.mol2).
   - Ruta al archivo .str CHARMM (drug.str).
   - Ruta al directorio que contiene los archivos de fuerza CHARMM36 (charmm36.ff).

Ejemplo de uso:
   python convert_charmm_to_gromacs.py RESNAME drug.mol2 drug.str charmm36.ff

2. El script realizará las siguientes acciones:
   - Leerá y analizará el archivo RTP CHARMM para obtener información sobre átomos, enlaces, ángulos y dihedros.
   - Leerá el archivo .mol2 para obtener las coordenadas de los átomos.
   - Generará un archivo .pdb inicial para la molécula.
   - Procesará el archivo .str CHARMM para obtener información sobre los parámetros de la molécula.
   - Escribirá un archivo .prm que contiene los parámetros de enlace y ángulo generados a partir de la información en el archivo .str CHARMM.
   - Generará un archivo .itp que contiene la topología molecular de la molécula.
   - Creará un archivo .top que debe incluirse en el sistema .top de GROMACS.

3. El script imprimirá mensajes informativos durante el proceso y proporcionará información sobre los archivos generados.

La estructura es:

1. Sección de Configuración:
   - Definición de los nombres de los archivos de entrada y salida.
   - Importación de módulos necesarios.

2. Función `check_versions(rtp_name, forcefield_doc)`:
   - Verifica las versiones de CGenFF y los archivos de topología CHARMM.

3. Sección Principal:
   - Lectura y procesamiento del archivo RTP CHARMM para obtener información sobre átomos, enlaces, ángulos y dihedros.
   - Lectura del archivo .mol2 para obtener las coordenadas de los átomos.
   - Generación de un archivo .pdb inicial para la molécula.
   - Procesamiento del archivo .str CHARMM para obtener información sobre los parámetros de la molécula.

4. Función `autogen_angl_dihe(self)`:
   - Genera ángulos y dihedros automáticamente basados en la conectividad de átomos.

5. Función `get_nonplanar_dihedrals(self, angl_params)`:
   - Identifica dihedros no planares en función de los parámetros de ángulo.

6. Función `write_gmx_itp(self, filename, angl_params)`:
   - Escribe un archivo .itp que contiene la topología molecular de la molécula.

7. Función `write_gmx_mol_top(filename, ffdir, prmfile, itpfile, molname)`:
   - Escribe un archivo .top que debe incluirse en el sistema .top de GROMACS.

8. Función `read_mol2_coor_only(self, filename)`:
   - Lee solo las coordenadas del archivo .mol2.

9. Función `write_pdb(self, f)`:
    - Escribe un archivo .pdb de la molécula.

10. Función `main()`:
    - Maneja la ejecución principal del script, incluyendo la llamada a las funciones anteriores.

11. Mensajes informativos:
    - El script proporciona mensajes informativos durante su ejecución para guiar al usuario y mostrar el progreso.


Nota: Asegúrese de que los archivos y directorios mencionados en los argumentos existan antes de ejecutar el script.

Recuerde consultar la documentación de GROMACS y CHARMM para comprender completamente cómo utilizar los resultados generados por este script en sus simulaciones.

""" 


class AtomGroup:
    def __init__(self):
        self.G = nx.Graph()
        self.name = ""
        self.natoms = 0
        self.nbonds = 0
        self.angles = []
        self.nangles = 0
        self.dihedrals = []
        self.ndihedrals = 0
        self.impropers = []
        self.nimpropers = 0
        self.coord = np.zeros((self.natoms, 3), dtype=float)

    def read_charmm_rtp(self, rtp_lines, atomtypes):
        self.G = nx.Graph()
        self.name = ""
        self.natoms = 0
        self.nbonds = 0
        self.angles = []
        self.nangles = 0
        self.dihedrals = []
        self.ndihedrals = 0
        self.impropers = []
        self.nimpropers = 0

        atm = {}

        for line in rtp_lines:
            if '!' in line:
                line = line[:line.find('!')]

            if line.startswith("RESI"):
                entry = re.split('\s+', line.lstrip())
                self.name = entry[1]

            if line.startswith("ATOM"):
                entry = re.split('\s+', line.lstrip())
                atm[self.natoms] = {'type': entry[2], 'resname': self.name, 'name': entry[1],
                                    'charge': float(entry[3]), 'mass': float(0.00), 'beta': float(0.0),
                                    'x': float(9999.9999), 'y': float(9999.9999), 'z': float(9999.9999),
                                    'segid': self.name, 'resid': '1'}

                for typei in atomtypes:
                    if typei[0] == atm[self.natoms]['type']:
                        atm[self.natoms]['mass'] = float(typei[1])
                        break

                self.G.add_node(self.natoms, atm[self.natoms])
                self.natoms = self.natoms + 1

            if line.startswith("BOND") or line.startswith("DOUB"):
                entry = re.split('\s+', line.rstrip().lstrip())
                num_bonds = int((len(entry) - 1) / 2)
                for bondi in range(0, num_bonds):
                    found1 = False
                    found2 = False
                    for i in range(0, self.natoms):
                        if atm[i]['name'] == entry[(bondi * 2) + 1]:
                            found1 = True
                            break
                    for j in range(0, self.natoms):
                        if atm[j]['name'] == entry[(bondi * 2) + 2]:
                            found2 = True
                            break
                    if not found1:
                        print("Error:atomgroup:read_charmm_rtp> Atomname not found in top", entry[(bondi * 2) + 1])
                    if not found2:
                        print("Error:atomgroup:read_charmm_rtp> Atomname not found in top", entry[(bondi * 2) + 2])
                    self.G.add_edge(i, j)
                    self.G[i][j]['order'] = '1'

        self.nimpropers = len(self.impropers)
        if self.ndihedrals > 0 or self.nangles > 0:
            print("WARNING:atomgroup:read_charmm_rtp> Autogenerating angl-dihe even though they are preexisting",
                  self.nangles, self.ndihedrals)
        self.autogen_angl_dihe()
        self.coord = np.zeros((self.natoms, 3), dtype=float)

    def autogen_angl_dihe(self):
        self.angles = []
        for atomi in range(0, self.natoms):
            nblist = []
            for nb in self.G.neighbors(atomi):
                nblist.append(nb)
            for i in range(0, len(nblist) - 1):
                for j in range(i + 1, len(nblist)):
                    var = [nblist[i], atomi, nblist[j]]
                    self.angles.append(var)
        self.nangles = len(self.angles)
        self.dihedrals = []
        for i, j in self.G.edges():
            nblist1 = []
            for nb in self.G.neighbors(i):
                if nb != j:
                    nblist1.append(nb)
            nblist2 = []
            for nb in self.G.neighbors(j):
                if nb != i:
                    nblist2.append(nb)
            if len(nblist1) > 0 and len(nblist2) > 0:
                for ii in range(0, len(nblist1)):
                    for jj in range(0, len(nblist2)):
                        var = [nblist1[ii], i, j, nblist2[jj]]
                        if var[0] != var[3]:
                            self.dihedrals.append(var)
        self.ndihedrals = len(self.dihedrals)

    def get_nonplanar_dihedrals(self, angl_params):
        nonplanar_dihedrals = []
        cutoff = 179.9
        for var in self.dihedrals:
            d1 = self.G.node[var[0]]['type']
            d2 = self.G.node[var[1]]['type']
            d3 = self.G.node[var[2]]['type']
            d4 = self.G.node[var[3]]['type']
            keep = 1
            for angl_param in angl_params:
                p1 = angl_param[0]
                p2 = angl_param[1]
                p3 = angl_param[2]
                eq = angl_param[3]
                if (d2 == p2 and ((d1 == p1 and d3 == p3) or (d1 == p3 and d3 == p1))):
                    if (eq > cutoff):
                        keep = -1
                        break
                if (d3 == p2 and ((d2 == p1 and d4 == p3) or (d2 == p3 and d4 == p1))):
                    if (eq > cutoff):
                        keep = -1
                        break
            if keep == 1:
                nonplanar_dihedrals.append(var)
        return nonplanar_dihedrals

    def write_gmx_itp(self, filename, angl_params):
        with open(filename, 'w') as f:
            f.write("; Created by cgenff_charmm2gmx.py\n")
            f.write("\n")
            f.write("[ moleculetype ]\n")
            f.write("; Name			   nrexcl\n")
            f.write("%s				 3\n" % self.name)
            f.write("\n")
            f.write("[ atoms ]\n")
            f.write(";	 nr		  type	resnr residue  atom   cgnr	   charge		mass  typeB    chargeB		massB\n")
            f.write("; residue	 1 %s rtp %s q	qsum\n" % (self.name, self.name))
            pairs14 = nx.Graph()
            for atomi in range(0, self.natoms):
                pairs14.add_node(atomi)
                f.write("%6d %10s %6s %6s %6s %6d %10.3f %10.3f   ;\n" %
                        (atomi + 1, self.G.node[atomi]['type'],
                         self.G.node[atomi]['resid'], self.name, self.G.node[atomi]['name'], atomi + 1,
                         self.G.node[atomi]['charge'], self.G.node[atomi]['mass']))
            f.write("\n")
            f.write("[ bonds ]\n")
            f.write(";	ai	  aj funct			  c0			c1			  c2			c3\n")
            for i, j in self.G.edges():
                f.write("%5d %5d	 1\n" % (i + 1, j + 1))
            f.write("\n")
            f.write("[ pairs ]\n")
            f.write(";	ai	  aj funct			  c0			c1			  c2			c3\n")
            for var in self.dihedrals:
                if len(nx.dijkstra_path(self.G, var[0], var[3])) == 4:
                    pairs14.add_edge(var[0], var[3])
            for i, j in pairs14.edges():
                f.write("%5d %5d	 1\n" % (i + 1, j + 1))
            f.write("\n")
            f.write("[ angles ]\n")
            f.write(";	ai	  aj	ak funct			c0			  c1			c2			  c3\n")
            for var in self.angles:
                f.write("%5d %5d %5d	5\n" % (var[0] + 1, var[1] + 1, var[2] + 1))
            f.write("\n")
            f.write("[ dihedrals ]\n")
            f.write(";	ai	  aj	ak	  al funct			  c0			c1			  c2			c3			  c4			c5\n")
            nonplanar_dihedrals = self.get_nonplanar_dihedrals(angl_params)
            for var in nonplanar_dihedrals:
                f.write("%5d %5d %5d %5d	 9\n" % (var[0] + 1, var[1] + 1, var[2] + 1, var[3] + 1))
            f.write("\n")
            if self.nimpropers > 0:
                f.write("[ dihedrals ]\n")
                f.write(";	ai	  aj	ak	  al funct			  c0			c1			  c2			c3\n")
                for var in self.impropers:
                    f.write("%5d %5d %5d %5d	 2\n" % (var[0] + 1, var[1] + 1, var[2] + 1, var[3] + 1))
                f.write("\n")

    def read_mol2_coor_only(self, filename):
        check_natoms = 0
        check_nbonds = 0
        atm = {}
        section = "NONE"
        
        with open(filename, 'r') as f:
            for line in f.readlines():
                secflag = False
                if line.startswith("@"):
                    secflag = True
                    section = "NONE"

                if (section == "NATO") and (not secflag):
                    entry = re.split('\s+', line.lstrip())
                    check_natoms = int(entry[0])
                    check_nbonds = int(entry[1])
                    if check_natoms != self.natoms:
                        print("Error in atomgroup.py: read_mol2_coor_only: no. of atoms in mol2 (%d) and top (%d) are unequal" % (
                        check_natoms, self.natoms))
                        print(
                            "Usually this means the specified residue name does not match between str and mol2 files")
                        exit()
                    if check_nbonds != self.nbonds:
                        print("Error in atomgroup.py: read_mol2_coor_only: no. of bonds in mol2 (%d) and top (%d) are unequal" % (
                        check_nbonds, self.nbonds))
                        exit()

                    section = "NONE"

                if (section == "MOLE") and (not secflag):
                    self.name = line.strip()
                    section = "NATO"

                if (section == "ATOM") and (not secflag):
                    entry = re.split('\s+', line.lstrip())
                    if len(entry) > 1:
                        atomi = int(entry[0]) - 1
                        self.G.node[atomi]['x'] = float(entry[2])
                        self.G.node[atomi]['y'] = float(entry[3])
                        self.G.node[atomi]['z'] = float(entry[4])
                        self.coord[atomi][0] = float(entry[2])
                        self.coord[atomi][1] = float(entry[3])
                        self.coord[atomi][2] = float(entry[4])

                if line.startswith("@<TRIPOS>MOLECULE"):
                    section = "MOLE"
                if line.startswith("@<TRIPOS>ATOM"):
                    section = "ATOM"
                if line.startswith("@<TRIPOS>BOND"):
                    section = "BOND"

    def write_pdb(self, f):
        for atomi in range(0, self.natoms):
            if len(self.G.node[atomi]['name']) > 4:
                print("error in atomgroup.write_pdb(): atom name > characters")
                exit()
            f.write("%-6s%5d %-4s %-4s%5s%12.3f%8.3f%8.3f%6.2f%6.2f\n" %
                    ("ATOM", atomi + 1, self.G.node[atomi]['name'], self.name, self.G.node[atomi]['resid'],
                     self.coord[atomi][0],
                     self.coord[atomi][1], self.coord[atomi][2], 1.0, self.G.node[atomi]['beta']))
        f.write("END\n")

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: RESNAME drug.mol2 drug.str charmm36.ff")
        sys.exit(1)

    mol_name = sys.argv[1]
    mol2_name = sys.argv[2]
    rtp_name = sys.argv[3]
    ffdir = sys.argv[4]
    atomtypes_filename = ffdir + "/atomtypes.atp"

    print("NOTE1: Code tested with python 2.7.3. Your version:", sys.version)
    print("\nNOTE2: Please be sure to use the same version of CGenFF in your simulations that was used during parameter generation:")
    check_versions(rtp_name, ffdir + "/forcefield.doc")
    print("\nNOTE3: In order to avoid duplicated parameters, do NOT select the 'Include parameters that are already in CGenFF' option when uploading a molecule into CGenFF.")

    atomtypes = read_gmx_atomtypes(atomtypes_filename)
    angl_params = []
    filelist = get_filelist_from_gmx_forcefielditp(ffdir, "forcefield.itp")
    for filename in filelist:
        anglpars = read_gmx_anglpars(filename)
        angl_params = angl_params + anglpars

    m = AtomGroup()
    rtplines = get_charmm_rtp_lines(rtp_name, mol_name)
    m.read_charmm_rtp(rtplines, atomtypes)

    m.read_mol2_coor_only(mol2_name)
    with open(mol_name.lower() + "_ini.pdb", 'w') as f:
        m.write_pdb(f)

    prmlines = get_charmm_prm_lines(rtp_name)
    params = parse_charmm_parameters(prmlines)
    write_gmx_bon(params, "", mol_name.lower() + ".prm")
    anglpars = read_gmx_anglpars(mol_name.lower() + ".prm")
    angl_params = angl_params + anglpars

    m.write_gmx_itp(mol_name.lower() + ".itp", angl_params)
    write_gmx_mol_top(mol_name.lower() + ".top", ffdir, mol_name.lower() + ".prm", mol_name.lower() + ".itp", mol_name)

    print("============ DONE ============")
    print("Conversion complete.")
    print("The molecule topology has been written to %s" % (mol_name.lower() + ".itp"))
    print("Additional parameters needed by the molecule are written to %s, which needs to be included in the system .top" % (
    mol_name.lower() + ".prm"))
    print("============ DONE ============")
