import urllib.request
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import base64
import os

# Clase CpuData, dispone de los siguientes métodos:
        # __attr_init__ --> Para inicializar las distintas propiedades del objeto
        # __init__ --> Para inicializar el objeto, se apoya en el método __attr_init__
        # store_data --> Se utiliza para para almacenar los datos de una CPU junto con sus imágenes
        # __get_b64_img --> Se utiliza para pasar a base64 una imágen en caso de que la queramos guardar en el dataset
        # __collect_data --> Se utiliza para recoger los datos de la página web, lo que permitirá luego almacenarlos
        # __download_url --> Es el método que baja el html de la página web para que se pueda tratar

class CpuData:

    # Se utiliza para inicializar las distintas propiedades que tendrá el objeto
    def __attr_init__(self):
        # Sería la url de donde sacamos la información
        self.url = ''
        self.plain_html = ''
        self.soup_html = None

        # Los distintos datos que puede tener una CPU
        self.cpu_properties = {
            'cpu_name': '',
            'cpu_logo': '',
            'socket': '',
            'foundry': '',
            'process_size': '',
            'transistors': '',
            'die_size': '',
            'package': '',
            'tcasemax': '',
            'tj_max': '',
            'frequency': '',
            'turbo_clock': '',
            'base_clock': '',
            'multiplier': '',
            'multiplier_unlocked': '',
            'voltage': '',
            'tdp': '',
            'fp32': '',
            'market': '',
            'production_status': '',
            'release_date': '',
            'codename': '',
            'generation': '',
            'part_number': '',
            'memory_support': '',
            'ecc_memory': '',
            'pci_express': '',
            'cores_num': '',
            'threads_num': '',
            'smp_cpus_num': '',
            'integrated_graphics': '',
            'cache_l1': '',
            'cache_l2': '',
            'cache_l3': '',
            'features_list': [],
            'imgs': {},
            'notes': '',
            'pl1': '',
            'pl2': '',
            'chipsets': '',
            'chipset': ''
        }

        # Son las distintas tablas que contienen los datos de una CPU dentro de la página web
        # Se deben cargar los datos de estas tablas para disponer de toda la información de la CPU
        self.standard_tables = ['Physical', 'Performance', 'Architecture', 'Cores', 'Cache']

        # Se trata de un diccionario que nos permite traducir los distintos campos de la página web de CPUs
        # a los distintos campos dentro de la propiedad cpu_properties que hemos definido anteriormente
        self.enum_properties = {
            'Socket:': 'socket',
            'Foundry:': 'foundry',
            'Process Size: ': 'process_size',
            'Transistors:': 'transistors',
            'Die Size:': 'die_size',
            'Package:': 'package',
            'tCaseMax:': 'tcasemax',
            'Frequency:': 'frequency',
            'Turbo Clock:': 'turbo_clock',
            'Base Clock:': 'base_clock',
            'Multiplier:': 'multiplier',
            'Multiplier Unlocked:': 'multiplier_unlocked',
            'Voltage:': 'voltage',
            'TDP:': 'tdp',
            'FP32:': 'fp32',
            'Market:': 'market',
            'Production Status:': 'production_status',
            'Release Date:': 'release_date',
            'Codename:': 'codename',
            'Generation:': 'generation',
            'Part#:': 'part_number',
            'Memory Support:': 'memory_support',
            'ECC Memory:': 'ecc_memory',
            'PCI-Express:': 'pci_express',
            '# of Cores:': 'cores_num',
            '# of Threads:': 'threads_num',
            'SMP # CPUs: ': 'smp_cpus_num',
            'Integrated Graphics:': 'integrated_graphics',
            'Cache L1: ': 'cache_l1',
            'Cache L2: ': 'cache_l2',
            'Cache L3: ': 'cache_l3',
            'tJMax:': 'tj_max',
            'PL1:': 'pl1',
            'PL2:': 'pl2',
            'Chipsets:': 'chipsets',
            'Chipset:': 'chipset'
        }

    # Utiliza el método __attr_init__ para inicializar las distintas propiedades del objeto
    # Además, lee la página web para la CPU de la que queremos descargar los datos
    def __init__(self, url):
        # Inicializamos los atributos
        self.__attr_init__()
        # En la propiedad url ponemos la url de la que queremos extraer la información
        self.url = urlparse(url)
        # Llamamos al método __download_url para leer el código html de la página y
        # pasarlo a la propiedad plain_html
        self.plain_html = self.__download_url(url)
        # Utilizamos BeautifulSoup para parsear el código html
        self.soup_html = BeautifulSoup(self.plain_html, 'html.parser')
        # Llamamos a la función que nos permite colectar los datos a partir del html ya parseado
        self.__collect_data()

    # Método utilizado para almacenar la información de CPU en el disco
    def store_data(self, path, include_headers, create_images, img_as_path):
        if include_headers and not os.path.isfile(path):
            headers = ",".join(self.cpu_properties.keys())
            with open(path, 'w') as f:
                f.write(headers + "\n")
        data = ''

        # Recorremos los distintos campos de la estructura cpu_properties
        # Es donde van a almacenar los distintos datos de la página
        for key in self.cpu_properties:
            writed_data = False
            # Si el campo es cpu_logo, guardamos el path donde vamos a guardar la imagen del logo
            if key == 'cpu_logo' and img_as_path:
                data = data + '"' + 'img/' + self.cpu_properties['cpu_name'].replace(' ', '_') + '/' + \
                       self.cpu_properties['cpu_name'].replace(' ', '_') + '_logo.png' + '"' + ','
                writed_data = True
            # Si se ha pulsado la opción de guardar las imágenes, almacenamos el logo
            if key == 'cpu_logo' and create_images:
                if self.cpu_properties['cpu_logo'] is not "":
                    if not os.path.isdir('img'):
                        os.mkdir('img')
                    if not os.path.isdir('img/'+self.cpu_properties['cpu_name'].replace(' ', '_')):
                        os.mkdir('img/'+self.cpu_properties['cpu_name'].replace(' ', '_'))
                    with open('img/' + self.cpu_properties['cpu_name'].replace(' ', '_') + '/' +
                              self.cpu_properties['cpu_name'].replace(' ', '_') + '_logo.png', "wb") as f:
                        f.write(base64.decodebytes(self.cpu_properties['cpu_logo']))
            # Hacemos lo mismo con el resto de imágenes de la página web
            # indicamos la ruta donde vamos a grabar las imágenes
            if key == 'imgs' and img_as_path:
                imgs_paths = {}
                for img in self.cpu_properties[key]:
                    imgs_paths[img] = 'img/' + self.cpu_properties['cpu_name'].replace(' ', '_') + '/' + \
                                      self.cpu_properties['cpu_name'].replace(' ', '_') + '_' + \
                                      img.replace(' ', '_') + '.png'
                data = data + '"' + str(imgs_paths) + '"' + ','
                writed_data = True
            # Bajamos las imágenes a la ruta que se haya indicado
            if key == 'imgs' and create_images:
                for img in self.cpu_properties[key]:
                    if not os.path.isdir('img'):
                        os.mkdir('img')
                    if not os.path.isdir('img/' + self.cpu_properties['cpu_name'].replace(' ', '_')):
                        os.mkdir('img/' + self.cpu_properties['cpu_name'].replace(' ', '_'))
                    with open('img/' + self.cpu_properties['cpu_name'].replace(' ', '_') + '/' +
                              self.cpu_properties['cpu_name'].replace(' ', '_') + '_' +
                              img.replace(' ', '_') + '.png', "wb") as f:
                        f.write(base64.decodebytes(self.cpu_properties[key][img]))
            if not writed_data:
                data = data + '"' + str(self.cpu_properties[key]) + '"' + ','
        data = data[0:-1]
        # En cada vuelta del bucle, almacenamos la información en el fichero de datos
        with open(path, 'a') as f:
            f.write(data + "\n")

    # Método para descargar una imagen y transformarla a base64
    @staticmethod
    def __get_b64_img(url):
        # Preparamos la url y la cabecera
        req = urllib.request.Request(
            url,
            data=None,
            headers={
                'User-Agent': 'UOC Test Bot. Img downloader. lgarciatar@uoc.edu & mrodrise@uoc.edu'
            }
        )

        # Descargamos la imagen
        img = urllib.request.urlopen(req, timeout=10).read()

        # Transformamos la imagen a base64
        b64_img = base64.b64encode(img)

        return b64_img

    # Este método recoge la información de la página web y rellena las propiedades del objeto
    # Implica conocer cómo está estructurada la página web, en base a los distintos tags podrá
    # recolecar los disintos datos cara a rellenar las propiedades del objeto
    def __collect_data(self):

        # Nos vamos al punto del html donde podremos comenzar a recoger los datos
        article = self.soup_html.find('article')

        # Creo una lista con todos los tags de tipo div
        article_div_list = article.find_all('div')

        # Recorro la lista y voy recogiendo los distintos valores
        for div in article_div_list:
            # Si el div tiene clases, revisamos las distintas clases ya que dentro estará la información

            if 'class' in div.attrs:

                # Si tiene la clase clearfix y no tiene la clase images, estamos en la zona de nombre y logo
                if 'clearfix' in div.attrs['class'] and 'images' not in div.attrs['class']:
                    for h1 in div.find_all('h1'):
                        if 'cpuname' in h1.attrs['class']:
                            self.cpu_properties['cpu_name'] = str(h1.string)
                    for img in div.find_all('img'):
                        if 'cpulogo' in img.attrs['class']:
                            self.cpu_properties['cpu_logo'] = self.__get_b64_img('{uri.scheme}://{uri.netloc}'.
                                                                                 format(uri=self.url) +
                                                                                 img.attrs['src'])
                # Si tiene la clase clearfix y tiene la clase images, estamos en la zona de imágenes
                # Por tanto, procedemos a descargarlas si el usuario lo ha solicitado
                if 'clearfix' in div.attrs['class'] and 'images' in div.attrs['class']:
                    for inner_div in div.findAll('div'):
                        if 'chip-image' in inner_div.attrs['class']:
                            src = inner_div.find('img', {"class": "chip-image--img"}).attrs['src']
                            if 'http' not in src:
                                img = self.__get_b64_img('{uri.scheme}://{uri.netloc}'.format(uri=self.url) + src)
                            else:
                                img = self.__get_b64_img(src)
                            name = str(inner_div.find('div', {"class": "chip-image--type"}).string)
                            self.cpu_properties['imgs'][name] = img

                # Se trataría de la zona donde están las tablas con la información de la CPU
                if 'sectioncontainer' in div.attrs['class']:
                    for section in div.find_all('section'):
                        if str(section.find('h1').string) in self.standard_tables:
                            table = section.find('table')
                            for row in table.findAll('tr'):
                                th = str(row.find('th').string)
                                td = str(row.find('td').text)

                                # Evaluamos el valor del campo de información, si no lo tenemos lo añadimos
                                # al fichero no_enum para que el usuario disponga también de estos datos
                                try:
                                    self.cpu_properties[self.enum_properties[th]] = td.strip().replace("\n", "")\
                                        .replace("\r", "")
                                except Exception as e:
                                    with open('no_enum', 'a') as f:
                                        f.write(th)
                        if str(section.find('h1').string) == 'Features':
                            for item in section.findAll('li'):
                                self.cpu_properties['features_list'].append(str(item.string).strip().replace("\n", ""))
                        if str(section.find('h1').string) == 'Notes':
                            text_container = section.find('td', {"class": "p"})
                            self.cpu_properties['notes'] = str(text_container.string).strip().replace("\n", "")

    # Este método se encarga de descargar el código html de la página web
    @staticmethod
    def __download_url(url):
        # Ponemos la cabecera e indicamos la url de la que vamos a descargar el código
        req = urllib.request.Request(
            url,
            data=None,
            headers={
                'User-Agent': 'UOC Test Bot. lgarciatar@uoc.edu & mrodrise@uoc.edu'
            }
        )

        # Hacemos la petición de descarga del código de la url
        html_doc = urllib.request.urlopen(req, timeout=10).read()

        # Devolvemos el código que hemos descargado
        return html_doc
