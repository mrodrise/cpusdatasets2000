from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
import time
import platform


def configurar_driver():

    # En caso de que se quieran añadir opciones se puede hacer aquí
    chrome_options = Options()
    # Una opción para evitar que no nos dejen hacer webscraping es no usar cabeceras
    chrome_options.add_argument("--headless")
    # Antes de iniciar el webdriver necesitamos saber si el sistema operativo es Linux, Mac o Windows
    # El path del ejecutable cambia para windows con respecto a Linux y Mac ya que necesita extensión .exe

    sistema = platform.system()
    print("Estamos en el sistema operativo", sistema)

    # Iniciamos en webdriver dependiendo del sistema operativo
    if sistema == "Windows":
        driver = webdriver.Chrome(executable_path="./chromedriver.exe", options = chrome_options)
    else:
        driver = webdriver.Chrome(executable_path="./chromedriver", options = chrome_options)

    return driver


def getInfoCPUs(driver, anio):
    # La página web detecta web scraping, bloqueando si detecta que se hacen muchas peticiones seguidas
    # Vamos a introducir un delay para evitar que nos bloqueen
    t0 = time.time()
    # Cargamos la página web para el año que nos han pasado
    driver.get(f"https://www.techpowerup.com/cpu-specs/?released={anio}&sort=name")
    # Esperamos a que cargue la página hasta el elemento que necesitamos
    try:
        WebDriverWait(driver, 5).until(lambda s: s.find_element_by_class_name("processors").is_displayed())
    except TimeoutException:
        print("ERROR - Excepción de tipo Time Out: No se ha podido cargar la página")
        return None

    # Vemos cuánto es el delay entre que lanzamos la petición y tenemos el resultado
    response_delay = time.time() - t0

    # Utilizamos BeautifulSoup para tratar con más facilidad la informaicón cargada
    soup = BeautifulSoup(driver.page_source, "lxml")

    # Utilizamos la variable i para tener un contador a modo de resumen de número de procesadores para ese año
    i = 0

    # Buscamos la tabla processors donde está el listado de procesadores con sus links a las páginas de detalle
    for course_page in soup.select("table.processors"):
        for course in course_page.select("a"):
            print(course['href'])
            i += 1

    print ("Se han encontrado un total de: ", i, " links")

    # Metemos un delay para evitar que la página nos bloquee
    time.sleep(10 * response_delay)

# *****************************************************
# *************** PARTE MAIN DEL CÓDIGO ***************
# *****************************************************

# Creamos el objeto de driver y lo inicializamos
driver = configurar_driver()

# Accedemos a la página principal donde está la información que queremos extraer
driver.get(f"https://www.techpowerup.com/cpu-specs/?sort=name")

# Esperamos a que cargue el elemento que necesitamos, en este caso es la tabla processors que contine
# la información de procesadores que necesitamos extraer

try:
    WebDriverWait(driver, 5).until(lambda s: s.find_element_by_class_name("processors").is_displayed())
except TimeoutException:
    print("ERROR - Excepción de tipo Time Out: No se ha podido cargar la página")

# Utilizamos BeautifulSoup con el parser que parece más extendido: lxml
soup = BeautifulSoup(driver.page_source, "lxml")

# Buscamos el elemento que contiend el id "released"
# El objetivo es leer de este selector todos los años para los que la página web tiene información

course_page = soup.find(id='released')

# Cargamos todos los años, buscando el tag option dentro del selector
# Ignoramos el primer valor de option ya que es para cargar los resultados más populares y queremos años
anios = []
i = 0
for course in course_page.find_all("option"):
    if i > 0:
        print(course['value'])
        anios.append(course['value'])
    i = i + 1

print("Años ", anios)

# Ya tenemos todos los años, recorremos la lista de años obtenemos la información que necesitamos por año
for anio in anios:
    print ("***************************")
    print ("Año a extraer", anio)
    print ("***************************")
    search_keyword = anio
    getInfoCPUs(driver, anio)

# close the driver.
driver.close()
