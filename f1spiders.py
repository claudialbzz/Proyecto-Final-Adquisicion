#-----PARTE 1:CRAWLER-----#
import scrapy
from scrapy.crawler import CrawlerProcess
import pandas as pd
import os
import io

class F1Spider(scrapy.Spider):
    name = 'F1_spider'

    def start_requests(self):
        """
        Esta función realiza un scrapy de las urls pedidas por el enunciado
        
        :param self: 
        """
        urls_years = [f'https://en.wikipedia.org/wiki/{i}_Formula_One_World_Championship' for i in range(2012,2025)] #Extraemos las urls por años guardándolas en una lista
        year = 2012

        for url in urls_years:
            yield scrapy.Request(url = url,callback=self.parse,meta = {'year':year}) #Pasamos como metadato el año para posteriormente guardar los csv 
            year += 1

    def parse(self,response):
        """
        Se encarga de obtener la tabla de Results and Standings y accede 
        a los enlaces que se encuentran en las celdas de la columna Report (apartados a) y b))
        
        :param self
        :param response: Obtenido de la función start_requests()
        """
        year = response.meta['year'] #Guardamos el metadato
        table_selector = response.css('table.wikitable.sortable tr')[1:] #Extraemos la tabla de la página que buscamos

        for table in table_selector:
            text = table.css('td::text').getall() #Obtenemos lo que serían los encabezados

            if not text: #Si no hay encabezados no nos vale
                continue

            url = None
            for urls in table.css('a'): #Vamos a seleccionar la etiqueta a que será la que contenga los enlaces
                texto = urls.css('::text').get() #Obtenemos el texto que se almancena en la etiqueta 

                if texto and 'Report' in texto: #Si ese texto coincide con Report, contendrá los enlaces que buscamos
                    url = urls.css('a::attr(href)').get() #Extraemos el enlace
                    race_name = url[11:] #Para obtener el nombre de la carrera hacemos slicing

                    if url: #Si existe enlace creamos el enlace final con urljoin (importado con scrapy)
                        url_final = response.urljoin(url) 
                        yield scrapy.Request(url = url_final,callback=self.parse_race,meta={'year':year,"race": race_name.strip()}) #Accedemos a los enlaces de Report
                        #pasando como metadato el año y el nombre de la carrera, para facilitar el almacenamiento de los ficheros

    def parse_race(self,response): 
        """
        Esta función se encarga de obtener la tabla de clasificaciones,convertirla en DataFrame
        y ese DataFrame convertirlo a csv guardándolo en una carpeta para cada año específico (apartados c) y d))
        
        :param self:
        :param response: Urls generadas por la función parse
        """
        year = response.meta['year'] #Almacenamos los metadatos
        race = response.meta['race']

        selectores = response.css('div.mw-heading, table.wikitable') #Seleccionamos los elementos con etiqueta div y table (Para obtener Race/Race classification y la tabla correspondiente)
        race_encontrado = False

        for elemento in selectores:
            titulo = elemento.css('h3::text').get() or '' #Obtenemos los textos con etiqueta h3
            titulo = titulo.strip()

            if 'Race classification' in titulo or titulo == 'Race': #Seleccionamos la tabla que vaya justo después de este título
                race_encontrado = True

            elif race_encontrado and elemento.css('table.wikitable'):
                tabla_html = elemento.get() #Obtenemos la tabla pedidan
                df = pd.read_html(io.StringIO(str(tabla_html))) #La convertimos en DataFrame
                if 'Time/Retired' in df[0].columns: #Nos aseguramos de que sea la correcta poniendo como condición que Time/Retired esté en la tabla
                    #(Evitamos filtrar tablas que aunque sean posteriores a nuestro título, no sean la que buscamos → Time/Retired es específica únicamente de la tabla que buscamos) 
                    tabla_final = df[0].iloc[:-1]  #Eliminamos la última fila (Contiene Source)
                    ultima_fila_str = tabla_final.iloc[-1].to_string() #Veremos si encontramos otra fila que sobra como Fastests Lap y la eliminamos en caso de que esté
                    
                    if 'fastest' in ultima_fila_str.lower():
                        tabla_final = tabla_final.iloc[:-1]


                    os.makedirs(f"data/{year}", exist_ok=True) #Creamos los directorios que se encuentran dentro de data y ponemos como nombre el año
                    tabla_final.to_csv(f"data/{year}/{race}.csv", index=False) #Convertimos el DataFrame a csv y lo guardamos en el directorio correspondiente a su año
                    self.log(f"Guardado: data/{year}/{race}.csv") #**Mensaje adicional para mostrar al usuario que ya se ha guardado ese archivo (ayuda Deepseek para facilitar visualización)

if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(F1Spider)
    process.start() 

