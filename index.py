#JAMV 
#Facultad de Psicología UNAM 
#Paciencia pa la ciencia 

from flask import Flask, render_template, request, send_from_directory, jsonify
import os
import pandas as pd
import networkx as nx
from networkx.algorithms import bipartite
import community as community_louvain
import pyreadstat
import shutil
import time


app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'sav'}
progress = {}
status = "Esperando datos..."

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

###########################################################################

@app.route('/', methods=['GET', 'POST'])
def home():
    global status
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)
            status = "Esperando a procesar..."
            process_file(filename)
            status = "Esperando datos..."  # Resetear el status después de procesar
            return render_template('home.html', files=os.listdir(app.config['UPLOAD_FOLDER']), status=status)
    return render_template('home.html', status=status)


############################################################################

@app.route('/progress')
def get_progress():
    filename = request.args.get('filename')
    return jsonify(progress.get(filename, "Procesando..."))

#############################################################################

def clear_upload_folder(keep_filename=None):
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                if not filename == keep_filename:
                    os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')

############################################################################

def process_file(filepath):
    global status
    filename = os.path.basename(filepath)
    status = f"Iniciando el procesamiento del archivo: {filename}"
    progress[filename] = status
    print(status)
    


    # Reiniciar estados
    progress.clear()  # Limpia el diccionario de progreso para evitar estados antiguos
    clear_upload_folder(keep_filename=filename)  # Limpia la carpeta, excepto el archivo actual
    status = f"Carpeta de subida limpiada, manteniendo: {filename}"
    progress[filename] = status
    print(status)

    # Actualizar estado inicial
    original_filename_base = os.path.splitext(filename)[0]
    _, file_extension = os.path.splitext(filepath)

    status = f"Leyendo el archivo con extensión {file_extension}..."
    progress[filename] = status
    print(status)
    
    if file_extension == '.csv':
        base = pd.read_csv(filepath)
    elif file_extension == '.xlsx':
        base = pd.read_excel(filepath, engine='openpyxl')
    elif file_extension == '.sav':
        base, meta = pyreadstat.read_sav(filepath)
    else:
        base = None
    
    if base is not None:
        status = "Archivo leído correctamente."
        progress[filename] = status
        print(status)
        
        status = "Transformando los datos..."
        progress[filename] = status
        print(status)
        baseT = pd.melt(base, id_vars=["Persona"])
        baseT["Item"] = baseT['variable'].astype(str) + "L" + baseT['value'].astype(str)
        
        status = "Creando grafo bipartito..."
        progress[filename] = status
        print(status)
        B = nx.Graph()
        B.add_nodes_from(baseT["Persona"].unique(), bipartite=0)
        B.add_nodes_from(baseT["Item"].unique(), bipartite=1)
        edges = baseT[["Persona", "Item"]].values.tolist()
        B.add_edges_from(edges)

        status = "Proyectando grafos..."
        progress[filename] = status
        print(status)
        Persona, Item = bipartite.sets(B)
        P = bipartite.weighted_projected_graph(B, Item)
        Q = bipartite.weighted_projected_graph(B, Persona)

        status = "Guardando archivos GEXF..."
        progress[filename] = status
        print(status)
        nx.write_gexf(B, os.path.join(app.config['UPLOAD_FOLDER'], f"{original_filename_base}_Bipartita_original.gexf"))
        status = f"Archivo guardado: {original_filename_base}_Bipartita_original.gexf"
        progress[filename] = status
        print(status)

        nx.write_gexf(P, os.path.join(app.config['UPLOAD_FOLDER'], f"{original_filename_base}_Proyeccion_Item.gexf"))
        status = f"Archivo guardado: {original_filename_base}_Proyeccion_Item.gexf"
        progress[filename] = status
        print(status)

        nx.write_gexf(Q, os.path.join(app.config['UPLOAD_FOLDER'], f"{original_filename_base}_Proyeccion_Persona.gexf"))
        status = f"Archivo guardado: {original_filename_base}_Proyeccion_Persona.gexf"
        progress[filename] = status
        print(status)

        status = "Detectando comunidades..."
        progress[filename] = status
        print(status)
        partition_p = community_louvain.best_partition(P)
        partition_q = community_louvain.best_partition(Q)

        status = "Guardando archivos CSV..."
        progress[filename] = status
        print(status)
        df_p = pd.DataFrame(list(partition_p.items()), columns=['Item', 'Community'])
        df_q = pd.DataFrame(list(partition_q.items()), columns=['Persona', 'Community'])

        df_p.to_csv(os.path.join(app.config['UPLOAD_FOLDER'], f'{original_filename_base}_Comunidades_Psicol.csv'), index=False)
        status = f"CSV guardado: {original_filename_base}_Comunidades_Psicol.csv"
        progress[filename] = status
        print(status)

        df_q.to_csv(os.path.join(app.config['UPLOAD_FOLDER'], f'{original_filename_base}_Comunidades_Personas.csv'), index=False)
        status = f"CSV guardado: {original_filename_base}_Comunidades_Personas.csv"
        progress[filename] = status
        print(status)
        
        status = f"Proceso completado con éxito para: {filepath}"
        progress[filename] = status
        print(status)
    else:
        status = "Formato de archivo no soportado o error en la carga del archivo."
        progress[filename] = status
        print(status)


#############################################################################

@app.route('/uploads/<filename>')
def download_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    else:
        return "Archivo no encontrado", 404

@app.route('/tutoriales')
def tutoriales():
    return render_template('tutoriales.html')

@app.route('/acerca_de')
def acerca_de():
    return render_template('acerca_de.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)











