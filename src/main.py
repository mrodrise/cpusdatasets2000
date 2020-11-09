from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
import time
import platform
import sys
# importamos robotparser que tiene utilidades para leer el fichero robots.txt
from urllib import robotparser

# Definimos en otro fichero la clase CpuData que a partir de una URL de una CPU,
# extraiga todos sus datos e imágenes, se utilizará más adelante en el bucle principal de extracción
# de los datos de las distintas CPUs.
from src.CpuData import CpuData


def driver_config():

    # En caso de que se quieran añadir opciones se puede hacer aquí
    chrome_options = Options()

    # Una opción para evitar que no nos dejen hacer webscraping es no usar cabeceras
    chrome_options.add_argument("--headless")

    # Antes de iniciar el webdriver necesitamos saber si el sistema operativo es Linux, Mac o Windows
    # El path del ejecutable cambia para windows con respecto a Linux y Mac ya que necesita extensión .exe
    os = platform.system()
    print("Detected OS:", os)

    # Iniciamos en webdriver dependiendo del sistema operativo
    if os == "Windows":
        inner_driver = webdriver.Chrome(executable_path="./chromedriver.exe", options=chrome_options)
    else:
        inner_driver = webdriver.Chrome(executable_path="./chromedriver", options=chrome_options)

    return inner_driver


def get_info_cpus(driver_inner, year_inner):
    # La página web detecta web scraping, bloqueando si detecta que se hacen muchas peticiones seguidas
    # Vamos a introducir un delay para evitar que nos bloqueen
    t0 = time.time()
    # Cargamos la página web para el año que nos han pasado
    driver_inner.get(f"https://www.techpowerup.com/cpu-specs/?released={year_inner}&sort=name")
    # Esperamos a que cargue la página hasta el elemento que necesitamos
    try:
        WebDriverWait(driver_inner, 5).until(lambda s: s.find_element_by_class_name("processors").is_displayed())
    except TimeoutException:
        print("ERROR - TimeoutException: Webpage can't be loaded.")
        return None

    # Vemos cuánto es el delay entre que lanzamos la petición y tenemos el resultado
    response_delay = time.time() - t0

    # Utilizamos BeautifulSoup para tratar con más facilidad la informaicón cargada
    soup_inner = BeautifulSoup(driver.page_source, "lxml")

    # Utilizamos la variable j para tener un contador a modo de resumen de número de procesadores para ese año
    j = 0

    # Buscamos la tabla processors donde está el listado de procesadores con sus links a las páginas de detalle
    for table in soup_inner.select("table.processors"):
        for detail_link in table.select("a"):
            print(detail_link['href'])

            # Creamos un objeto de tipo CpuData y lo inicializamos con la URL de la que extraer la información
            cpu = CpuData('https://www.techpowerup.com'+detail_link['href'])

            # Almacenamos los datos que hemos extraido de esa url
            cpu.store_data(dataset_path, include_headers, create_images, img_as_path)

            j += 1
            # Tenemos que poner tiempos de espera ya que el servidor detecta acciones muy seguidas desde una misma IP
            # Estos tiempos de espera se han establecido por prueba y error, en base a las distintas ejecuciones realiadas
            time.sleep(2*60)

            # Cada 100 extracciones debemos meter un tiempo de espera prudencial para que el servidor no nos bloquee
            if j % 100 == 0:
                time.sleep(5*60)

    print("A total of: ", j, " links where found.")

    # Procedemos a meter un tiempo de espera prudencial en base al tiempo de respuesta del servidor.
    # Así evitamos errores de tipo 423
    time.sleep(10 * response_delay)

# *****************************************************
# *************** PARTE MAIN DEL CÓDIGO ***************
# *****************************************************

if __name__ == '__main__':

    # Antes de comenzar necesitamos saber si el administrador del sitio da permiso para bajar los datos
    # Utilizamos un parser que nos ayude a leer el fichero robots.txt
    rp = robotparser.RobotFileParser()

    # Establecemos como url donde se encuentra el fichero robots.txt
    rp.set_url("https://www.techpowerup.com/robots.txt")

    # Leemos el fichero robots.txt
    rp.read()

    # Utilizando el parser vemos si para cualquier tipo de agente está permitido bajarse los datos
    # En el momento en que se hizo este código se podía bajar la página que nos interesa para
    # cualquier tipo de agente menos para SentiBot
    if (rp.can_fetch("*", "https://www.techpowerup.com/cpu-specs/?sort=name") == False):
        # Si el fichero robots.txt indica que no podemos bajar esa página, entonces finalizamos el programa
        print("The administrator of the site doesn't allow to download this data, the program will finish")
        sys.exit()

    # Creamos el objeto de driver y lo inicializamos
    driver = driver_config()

    # Accedemos a la página principal donde está la información que queremos extraer
    driver.get(f"https://www.techpowerup.com/cpu-specs/?sort=name")

    # Esperamos a que cargue el elemento que necesitamos, en este caso es la tabla processors que contine
    # la información de procesadores que necesitamos extraer

    try:
        WebDriverWait(driver, 5).until(lambda s: s.find_element_by_class_name("processors").is_displayed())
    except TimeoutException:
        print("ERROR - TimeoutException: Webpage can't be loaded.")

    # Utilizamos BeautifulSoup con el parser que parece más extendido: lxml
    soup = BeautifulSoup(driver.page_source, "lxml")

    # Buscamos el elemento que contiend el id "released"
    # El objetivo es leer de este selector todos los años para los que la página web tiene información
    course_page = soup.find(id='released')

    # Cargamos todos los años, buscando el tag option dentro del selector
    # Ignoramos el primer valor de option ya que es para cargar los resultados más populares y queremos años
    years = []
    i = 0
    for year_selector in course_page.find_all("option"):
        if i > 0:
            # print(year_selector['value'])
            years.append(year_selector['value'])
        i = i + 1

    print("Years ", years)

    # Preguntamos al usuario en qué carpeta quiere guardar la información.
    # Si pulsa D o pulsa enter, entonces creará el dataset en el directorio actual

    dataset_path = input("Default path (\"D\") or custom:")
    if dataset_path == "D" or len(dataset_path) < 2:
        dataset_path = 'dataset.csv'

    # Se le pregunta al usuario si quiere que las imágenes las guardemos en una carpeta o si prefiere
    # que las guardemos en un campo de dataset en formato bs4.
    img_as_path = input("Img as path in dataset (\"Y\") or as BS4 (\"N\") (BS4 could lead to broken lines in dataset):")
    if img_as_path == 'N':
        img_as_path = False
    else:
        img_as_path = True

    # Preguntamos al usuario si quiere que generemos las imágenes o no
    create_images = input("Generate images (\"Y\"/\"N\"):")
    if create_images == "N":
        create_images = False
    else:
        create_images = True

    # Preguntamos al usuario si quiere que se incluyan headers
    include_headers = input("Include headers (\"Y\"/\"N\"):")
    if include_headers == "N":
        include_headers = False
    else:
        include_headers = True

    # Preguntamos al usuario qué años quiere que extraigamos de la página web
    # Si pulsa enter, se bajará todos los años
    selected_years = input("As default dataset will contain all the loaded years, if you prefer to pick just some "
                           "years write them separated by coma for example (2010,2011,2012):")

    # selected_years es un string, miramos que el usuario al menos haya introducido 2 caracteres
    if len(selected_years) > 2:
        selected_years_list = selected_years.split(',')
        selected_years_list_clean = []
        # Revisamos que los años introducidos estén dentro del rango de años de la lista de años de la página web
        for year in selected_years_list:
            if year in years and year not in selected_years_list_clean:
                selected_years_list_clean.append(year)
            else:
                print('Year '+year+' has been removed, incorrect input or not available.')
        # Si se comprueba después de hacer limpieza que no hay años válidos, se cargan todos
        if len(selected_years_list_clean) < 1:
            print('Not even 1 year was available, all years will be downloaded.')
            selected_years = None
    else:
        # En caso de que lo haya dejado vacío o bien introducido 2 caracteres o menos, entendemos
        # que se quieren descargar todos los años
        selected_years = None

    # Ya tenemos todos los años que se quieren extraer por parte del usuario
    # Recorremos la lista de años obtenemos la información que necesitamos por año
    for year in years:
        print("***************************")
        print("Year to load: ", year)
        print("***************************")
        search_keyword = year

        # Esta es la función que hemos creado para extraer la información por año
        get_info_cpus(driver, year)

    # Cerramos el driver que habíamos creado
    driver.close()

    
