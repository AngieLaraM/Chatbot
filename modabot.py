import os
import nltk
import ssl
import streamlit as st
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from googletrans import Translator
import openai
from PIL import Image
import datetime
import requests

def configure():
    openai.api_key = st.secrets['api_key']

ssl._create_default_https_context = ssl._create_unverified_context
nltk.data.path.append(os.path.abspath("nltk_data"))
nltk.download('punkt')

intents = [
    {
        "tag": "saludo",
        "patterns": ["Hola", "Hola qué tal", "Hey", "Buenos días", "Buenas tardes", "Buenas noches"],
        "responses": ["¡Hola! ¿En qué puedo ayudarte hoy?", 
                      "¡Hola! ¿Qué te trae por aquí hoy?", 
                      "¡Hola! ¿Cómo puedo asistirte con tus necesidades de moda?", 
                      "¡Hey! ¿Listo para hablar de moda?", "¡Buenos días! ¿En qué puedo ayudarte hoy?", 
                      "¡Buenas tardes! ¿Cómo puedo asistirte con tus necesidades de moda?", 
                      "¡Buenas noches! ¿Qué te trae por aquí hoy?"]
    },

    {
        "tag": "adiós",
        "patterns": ["Adiós", "Hasta luego", "Chao", "Cuídate", "Bye", "Gracias"],
        "responses": ["Adiós", "Hasta luego", "Cuídate"]
    },

    {
        "tag": "pregunta",
        "patterns": ["¿Cómo estás?", "¿Qué tal te encuentras el día de hoy?", "¿Cómo vas?", "como estas", "como vas"],
        "responses": ["Hola! Estoy programado para estar siempre en mi mejor estado de ánimo. ¿Y tú cómo estás?", 
                      "Gracias por preguntar, estoy en línea y listo para ayudarte en lo que necesites", 
                      "Estoy genial, gracias por preguntar. Espero que tú también estés teniendo un buen día ¿Puedo ayudarte en algo en particular?", 
                      "Estoy funcionando a la perfección como siempre. ¿Y tú cómo estás hoy"]
    },

    {
        "tag": "ayuda",
        "patterns": ["Help", "¿Me puedes ayudar?", "Necesito ayuda", "Ayuda por favor", "Ayuda"],
        "responses": ["Claro, estoy aquí para ayudarte. ¿Qué necesitas?", 
                      "Por supuesto, ¿en qué puedo ayudarte?", 
                      "Estoy aquí para asistirte. ¿Qué necesitas?"]
    },
           
    {
        "tag": "color",
        "patterns": ["¿Cuál es tu color favorito?", "¿Qué colores están de moda?", "¿Qué color debo usar?", "¿Qué colores combinan bien?", "Que colores estan de moda", "Que colores me recomiendas"],
        "responses": ["Como chatbot, realmente no tengo un color favorito, pero te puedo decir que algunos colores populares esta temporada son los pasteles, colores brillantes y neutros.", 
                      "En este momento, los colores llamativos y brillantes están muy de moda. Piensa en naranjas vibrantes, rosas y amarillos.", 
                      "El color que deberías usar depende de tu tono de piel, la ocasión y tus preferencias personales. Algunos consejos generales: para un evento formal, opta por colores neutros como negro, blanco y gris. Para un evento casual, prueba colores brillantes.", 
                      "Algunos colores que combinan bien entre sí son negro y blanco, azul marino y beige, y rosa y gris."]
    },
        
       
    {
        "tag": "accesorios",
        "patterns": ["¿Cuáles son algunos accesorios de moda?", "¿Cómo puedo complementar mi outfit?", "¿Qué tipo de joyas debo usar?", "Accesorios de moda", "Accesorios"],
        "responses": ["Algunos accesorios de moda en este momento incluyen collares de cadena gruesa, accesorios para el cabello como diademas y scrunchies, y aretes llamativos.", 
                      "Para complementar tu outfit, piensa en la ocasión y el estilo que quieres transmitir. Para un look casual, prueba a superponer collares o añadir un sombrero. Para un look formal, opta por una pieza de joyería llamativa como un collar o aretes.", 
                      "El tipo de joyas que deberías usar depende de la ocasión y tu estilo personal. Algunas piezas clásicas que funcionan para muchas ocasiones incluyen aretes pequeños, un collar delicado y una pulsera sencilla."]
    },
        
    {
        "tag": "presupuesto",
        "patterns": ["¿Cuáles son algunas opciones de moda asequibles?", "¿Cómo puedo ahorrar dinero en ropa?", "¿Cuál es un buen presupuesto para la ropa?", "presupuesto"],
        "responses": ["¡Hay muchas opciones de moda asequibles por ahí! Prueba a comprar en tiendas de descuento como Koaj o minoristas en línea como ASOS y Boohoo. También puedes revisar tiendas de segunda mano", 
                      "Para ahorrar dinero en ropa, intenta comprar durante las ventas o eventos de liquidación, y siempre verifica cupones y códigos promocionales antes de realizar una compra. También puedes probar a comprar ropa de segunda mano o alquilarla para ocasiones especiales.", 
                      "Un buen presupuesto para ropa depende de tus ingresos y preferencias personales. Como regla general, intenta no gastar más del 5-10 porciento de tus ingresos en ropa."]
        
    },
    
    {
        "tag": "zapatos",
        "patterns": ["¿Cuáles son algunos estilos populares de zapatos?", "¿Cómo elijo los zapatos adecuados para un atuendo?", "¿Qué tipo de zapatos debo usar para un evento formal?", "Zapatos"],
        "responses": ["Algunos estilos de zapatos populares en este momento incluyen zapatillas gruesas, mocasines y botines.", 
                      "Al elegir zapatos para un atuendo, considera la ocasión, el estilo que buscas y los colores y texturas de tu atuendo. Por ejemplo, si llevas un atuendo casual, las zapatillas o sandalias podrían ser una buena opción. Si buscas un look más elegante, prueba con tacones o botines.", 
                      "Para un evento formal, generalmente es mejor usar zapatos cerrados como zapatos de tacón o zapatos planos elegantes. Evita usar zapatillas o sandalias a menos que el evento sea específicamente casual."]
    },

    {
        "tag": "abrigos",
        "patterns": ["¿Cuáles son algunos abrigos de moda?", "¿Cómo puedo lucir elegante con un abrigo?", "¿Qué tipo de abrigo debo usar en invierno?", "Moda de abrigos", "Abrigos", "Recomiendame abrigos", "¿Cuáles son algunas chaquetas de moda?", "¿Cómo puedo lucir elegante con una chaqueta?", "¿Qué tipo de chaqueta debo usar en invierno?", "Moda de chaquetas", "Chaquetas", "Recomiendame chaquetas"],
        "responses": ["Algunos abrigos de moda en este momento incluyen el abrigo de lana con corte recto, la gabardina clásica y el abrigo de piel sintética.",
                      "Para lucir elegante con un abrigo, elige uno que se ajuste bien a tu cuerpo y tenga detalles sofisticados como botones dorados o un cinturón. Combínalo con prendas a juego y unos tacones altos.",
                      "En invierno, es recomendable usar un abrigo que te mantenga abrigado. Opta por un abrigo acolchado, un plumífero o una parka con capucha para protegerte del frío."]
    },

    {
        "tag": "pantalones",
        "patterns": ["¿Cuáles son algunos pantalones de moda?", "¿Cómo puedo combinar mis pantalones?", "¿Qué tipo de pantalón debo usar para ocasiones formales?", "Moda de pantalones", "Pantalones"],
        "responses": ["Algunos pantalones de moda en este momento incluyen los pantalones de tiro alto y pierna ancha, los pantalones cortos de ciclista y los pantalones cargo.",
                      "Para combinar tus pantalones, considera el estilo y la ocasión. Para un look casual, puedes combinar unos pantalones de mezclilla con una camiseta y zapatillas. Para un look más elegante, elige unos pantalones de vestir y combínalos con una blusa o una camisa formal y tacones.",
                      "Para ocasiones formales, es recomendable usar pantalones de vestir o pantalones de corte recto en colores neutros como el negro, el gris o el azul marino. Combínalos con una blusa o una camisa elegante y añade unos zapatos de vestir."]
    },
 
    {
        "tag": "gafas",
        "patterns": ["¿Cuáles son algunos estilos de gafas de moda?", "¿Cómo puedo elegir las gafas adecuadas para mi rostro?", "¿Qué tipo de gafas debo usar para proteger mis ojos del sol?", "Moda de gafas", "Gafas"],
        "responses": ["Algunos estilos de gafas de moda en este momento incluyen las gafas de sol estilo aviador, las gafas de pasta con montura gruesa y las gafas cat-eye.",
                      "Para elegir las gafas adecuadas para tu rostro, ten en cuenta la forma de tu cara. Por ejemplo, si tienes una cara redonda, las gafas cuadradas o rectangulares pueden ayudar a equilibrar tus rasgos. Si tienes una cara angular, las gafas redondas suavizarán tus líneas.",
                      "Para proteger tus ojos del sol, es recomendable usar gafas de sol con protección UV. Busca gafas con lentes oscuros y de alta calidad que bloqueen el 100% de los rayos UVA y UVB. Además, elige un estilo que se ajuste a tu rostro y refleje tu personalidad."]
    },
 
    {
        "tag": "sombreros",
        "patterns": ["¿Cuáles son algunos sombreros de moda?", "¿Cómo puedo lucir elegante con un sombrero?", "¿Qué tipo de sombrero debo usar en verano?", "Moda de sombreros", "Sombreros"],
        "responses": ["Algunos sombreros de moda en este momento incluyen el sombrero fedora, el sombrero de ala ancha y el sombrero de paja estilo boater.",
                      "Para lucir elegante con un sombrero, elige uno que se ajuste bien a tu cabeza y complemente tu atuendo. Combínalo con prendas a juego y accesorios que resalten tu estilo personal. Recuerda mantener una actitud segura y segura al usarlo.",
                      "En verano, es recomendable usar sombreros que te protejan del sol. Opta por sombreros de ala ancha, sombreros de paja o sombreros estilo fedora con materiales transpirables para mantenerte fresco y protegido del sol mientras disfrutas del aire libre."]
    },
 
    {
        "tag": "colores_primarios",
        "patterns": ["¿Cuáles son algunos colores primarios de moda?", "¿Cómo puedo combinar colores primarios en mi outfit?", "¿Qué colores primarios son más populares esta temporada?", "Moda de colores primarios", "Colores primarios"],
        "responses": ["Algunos colores primarios de moda en este momento incluyen el rojo intenso, el azul eléctrico y el amarillo brillante.",
                      "Para combinar colores primarios en tu outfit, puedes seguir algunas pautas. Una opción es crear un contraste llamativo combinando dos colores primarios en prendas o accesorios. Otra opción es utilizar un color primario como punto focal y combinarlo con colores neutros para equilibrar el conjunto.",
                      "Esta temporada, los colores primarios que están más populares son el rojo vibrante, el azul profundo y el amarillo soleado. Estos colores añaden un toque audaz y energético a cualquier atuendo."]
    },
    
    {
        "tag": "colores_combinan_amarillo",
        "patterns": ["¿Qué colores combinan bien con el amarillo?", "¿Cómo puedo combinar el amarillo en mi outfit?", "¿Qué colores puedo usar para resaltar el amarillo?", "Combinaciones de colores con amarillo", "Colores que combinan con amarillo"],
        "responses": ["El amarillo es un color vibrante que combina bien con varios colores. Algunas opciones para combinar el amarillo son: combinarlo con blanco para crear un look fresco y luminoso, combinarlo con azul para un contraste llamativo, combinarlo con gris para un aspecto moderno y sofisticado, y combinarlo con tonos tierra como marrón o beige para una combinación cálida y terrosa.",
                      "Para combinar el amarillo en tu outfit, puedes optar por usar prendas amarillas como prenda principal y combinarlas con accesorios en colores neutros como blanco, gris o negro. También puedes usar el amarillo como un toque de color en tu atuendo, combinándolo con prendas en tonos neutros o en colores complementarios.",
                      "Si quieres resaltar el amarillo, puedes combinarlo con colores que contrasten. Por ejemplo, puedes usar el amarillo con tonos morados para crear un contraste vibrante y llamativo. También puedes combinarlo con tonos verdes para una combinación fresca y primaveral."]
    },
 
    {
        "tag": "colores_combinan_azul",
        "patterns": ["¿Qué colores combinan bien con el azul?", "¿Cómo puedo combinar el azul en mi outfit?", "¿Qué colores puedo usar para resaltar el azul?", "Combinaciones de colores con azul", "Colores que combinan con azul"],
        "responses": ["El azul es un color versátil que combina bien con diversos colores. Algunas opciones para combinar el azul son: combinarlo con blanco para crear un look fresco y náutico, combinarlo con gris para un aspecto elegante y sofisticado, combinarlo con amarillo para un contraste vibrante y alegre, y combinarlo con tonos tierra como beige o marrón para una combinación armoniosa y terrosa.",
                      "Para combinar el azul en tu outfit, puedes usar prendas azules como base y combinarlas con accesorios en tonos neutros como blanco, gris o negro. También puedes crear combinaciones de azul con diferentes tonalidades, como mezclar azul marino con azul claro o azul turquesa.",
                      "Si quieres resaltar el azul, puedes combinarlo con colores que contrasten. Por ejemplo, puedes usar el azul con tonos anaranjados para crear un contraste cálido y llamativo. También puedes combinarlo con tonos rosados para una combinación suave y femenina."]
    },
 
    {
        "tag": "colores_combinan_rojo",
        "patterns": ["¿Qué colores combinan bien con el rojo?", "¿Cómo puedo combinar el rojo en mi outfit?", "¿Qué colores puedo usar para resaltar el rojo?", "Combinaciones de colores con rojo", "Colores que combinan con rojo"],
        "responses": ["El rojo es un color audaz y llamativo que combina bien con varios colores. Algunas opciones para combinar el rojo son: combinarlo con blanco para crear un look clásico y elegante, combinarlo con negro para un contraste fuerte y sofisticado, combinarlo con tonos neutros como gris o beige para una combinación más suave, y combinarlo con tonos dorados o plateados para un toque de glamour.",
                      "Para combinar el rojo en tu outfit, puedes usar prendas rojas como prenda principal y combinarlas con accesorios en tonos neutros para equilibrar el conjunto. También puedes utilizar el rojo como un toque de color en tu atuendo, combinándolo con prendas en tonos neutros o en colores complementarios.",
                      "Si quieres resaltar el rojo, puedes combinarlo con colores que contrasten. Por ejemplo, puedes usar el rojo con tonos verdes para crear un contraste llamativo y vibrante. También puedes combinarlo con tonos rosados para una combinación femenina y romántica."]
    },
 
    {
        "tag": "colores_combinan_negro",
        "patterns": ["¿Qué colores combinan bien con el negro?", "¿Cómo puedo combinar el negro en mi outfit?", "¿Qué colores puedo usar para resaltar el negro?", "Combinaciones de colores con negro", "Colores que combinan con negro"],
        "responses": ["El negro es un color versátil que combina bien con una amplia gama de colores. Algunas opciones para combinar el negro son: combinarlo con blanco para crear un look clásico y elegante, combinarlo con tonos pastel para una combinación suave y delicada, combinarlo con colores brillantes como rojo o amarillo para un contraste audaz, y combinarlo con tonos metálicos como plateado o dorado para un toque de sofisticación.",
                      "Para combinar el negro en tu outfit, puedes utilizarlo como base y combinarlo con accesorios en colores vivos para crear un contraste llamativo. También puedes crear combinaciones en blanco y negro para un look elegante y minimalista, o combinar el negro con diferentes tonalidades de grises para un conjunto sofisticado y monocromático.",
                      "Si quieres resaltar el negro, puedes combinarlo con colores brillantes o vibrantes. Por ejemplo, puedes agregar un toque de color con accesorios en tonos llamativos como rojo, azul eléctrico o verde esmeralda. También puedes combinar el negro con estampados audaces para crear un impacto visual."]
    },
 
    {
        "tag": "colores_combinan_blanco",
        "patterns": ["¿Qué colores combinan bien con el blanco?", "¿Cómo puedo combinar el blanco en mi outfit?", "¿Qué colores puedo usar para resaltar el blanco?", "Combinaciones de colores con blanco", "Colores que combinan con blanco"],
        "responses": ["El blanco es un color neutro y versátil que combina bien con una amplia variedad de colores. Algunas opciones para combinar el blanco son: combinarlo con negro para un look clásico y elegante, combinarlo con tonos pastel para una combinación suave y delicada, combinarlo con colores brillantes como rojo o amarillo para un contraste audaz, y combinarlo con tonos tierra como beige o marrón para una combinación cálida y natural.",
                      "Para combinar el blanco en tu outfit, puedes utilizarlo como base y combinarlo con colores llamativos para crear un contraste vibrante. También puedes crear combinaciones en blanco y negro para un look sofisticado y moderno, o utilizar tonos neutros como gris o beige para una combinación elegante y armoniosa.",
                      "Si quieres resaltar el blanco, puedes combinarlo con colores vivos o intensos. Por ejemplo, puedes agregar accesorios en tonos brillantes como azul eléctrico, fucsia o naranja para crear un impacto visual. También puedes combinar el blanco con estampados coloridos para agregar dinamismo a tu outfit."]
    },
 
    {
        "tag": "colores_combinan_verde",
        "patterns": ["¿Qué colores combinan bien con el verde?", "¿Cómo puedo combinar el verde en mi outfit?", "¿Qué colores puedo usar para resaltar el verde?", "Combinaciones de colores con verde", "Colores que combinan con verde"],
        "responses": ["El verde es un color fresco y versátil que combina bien con diferentes tonalidades. Algunas opciones para combinar el verde son: combinarlo con blanco para un look fresco y luminoso, combinarlo con tonos tierra como beige o marrón para una combinación natural, combinarlo con tonos neutros como gris o negro para un contraste moderno, y combinarlo con tonos complementarios como rosa o morado para una combinación audaz.",
                      "Para combinar el verde en tu outfit, puedes utilizarlo como prenda principal y combinarlo con colores neutros en accesorios o prendas complementarias. También puedes crear combinaciones tonales con diferentes tonalidades de verde, o utilizar estampados que incluyan verde en su diseño.",
                      "Si quieres resaltar el verde, puedes combinarlo con colores que contrasten o complementen. Por ejemplo, puedes agregar toques de color con accesorios en tonos naranja o amarillo para crear un contraste vibrante. También puedes combinar el verde con tonos azules o turquesas para una combinación fresca y armoniosa."]
    },
 
    {
        "tag": "colores_combinan_naranja",
        "patterns": ["¿Qué colores combinan bien con el naranja?", "¿Cómo puedo combinar el naranja en mi outfit?", "¿Qué colores puedo usar para resaltar el naranja?", "Combinaciones de colores con naranja", "Colores que combinan con naranja"],
        "responses": ["El naranja es un color cálido y vibrante que combina bien con varios colores. Algunas opciones para combinar el naranja son: combinarlo con tonos neutros como blanco o beige para una combinación equilibrada, combinarlo con tonos tierra como marrón o verde oliva para una combinación terrosa, combinarlo con tonos complementarios como azul o morado para un contraste llamativo, y combinarlo con tonos metálicos como dorado o cobre para un toque de elegancia.",
                      "Para combinar el naranja en tu outfit, puedes utilizarlo como prenda principal y combinarlo con colores neutros en accesorios o prendas complementarias. También puedes crear combinaciones audaces combinando el naranja con otros colores vivos como amarillo o rojo, o utilizar tonalidades más suaves de naranja en combinación con tonos pastel para un look delicado y femenino.",
                      "Si quieres resaltar el naranja, puedes combinarlo con colores que contrasten o resalten su vibración. Por ejemplo, puedes agregar toques de color con accesorios en tonos azules o verdes para crear un contraste refrescante. También puedes combinar el naranja con tonos dorados o metálicos para un aspecto llamativo y glamoroso."]
    },
 
    {
        "tag": "colores_combinan_morado",
        "patterns": ["¿Qué colores combinan bien con el morado?", "¿Cómo puedo combinar el morado en mi outfit?", "¿Qué colores puedo usar para resaltar el morado?", "Combinaciones de colores con morado", "Colores que combinan con morado"],
        "responses": ["El morado es un color sofisticado y elegante que combina bien con diferentes tonalidades. Algunas opciones para combinar el morado son: combinarlo con tonos neutros como blanco o gris para un look suave y equilibrado, combinarlo con tonos plateados o dorados para un toque de glamour, combinarlo con tonos rosa o fucsia para una combinación femenina y audaz, y combinarlo con tonos verdes para un contraste fresco y vibrante.",
                      "Para combinar el morado en tu outfit, puedes utilizarlo como prenda principal y combinarlo con colores neutros en accesorios o prendas complementarias. También puedes crear combinaciones tonales con diferentes tonalidades de morado, o utilizar estampados que incluyan morado en su diseño.",
                      "Si quieres resaltar el morado, puedes combinarlo con colores que contrasten o complementen. Por ejemplo, puedes agregar toques de color con accesorios en tonos amarillos o naranjas para crear un contraste audaz. También puedes combinar el morado con tonos metálicos como el plata o el oro para un aspecto elegante y sofisticado."]
    },
 
    {
        "tag": "colores_combinan_cafe",
        "patterns": ["¿Qué colores combinan bien con el café?", "¿Cómo puedo combinar el café en mi outfit?", "¿Qué colores puedo usar para resaltar el café?", "Combinaciones de colores con café", "Colores que combinan con café"],
        "responses": ["El café es un color cálido y versátil que combina bien con varios colores. Algunas opciones para combinar el café son: combinarlo con tonos neutros como blanco, beige o gris para una combinación elegante y sofisticada, combinarlo con tonos tierra como verde oliva o marrón oscuro para una combinación natural y armoniosa, combinarlo con tonos cálidos como naranja o amarillo para un contraste vibrante, y combinarlo con tonos metálicos como dorado o cobre para un toque de lujo.",
                      "Para combinar el café en tu outfit, puedes utilizarlo como prenda principal y combinarlo con colores neutros en accesorios o prendas complementarias. También puedes crear combinaciones tonales utilizando diferentes tonalidades de café, o utilizar estampados que incluyan tonos café en su diseño.",
                      "Si quieres resaltar el café, puedes combinarlo con colores que contrasten o complementen. Por ejemplo, puedes agregar toques de color con accesorios en tonos azules o verdes para crear un contraste refrescante. También puedes combinar el café con tonos dorados o metálicos para un aspecto sofisticado y elegante."]
    },
 
    {
        "tag": "colores_combinan_rosado",
        "patterns": ["¿Qué colores combinan bien con el rosado?", "¿Cómo puedo combinar el rosado en mi outfit?", "¿Qué colores puedo usar para resaltar el rosado?", "Combinaciones de colores con rosado", "Colores que combinan con rosado"],
        "responses": ["El rosado es un color delicado y femenino que combina bien con diferentes tonalidades. Algunas opciones para combinar el rosado son: combinarlo con tonos neutros como blanco o gris para un look suave y elegante, combinarlo con tonos pastel como celeste o lavanda para una combinación dulce y armoniosa, combinarlo con tonos metálicos como plateado o dorado para un toque de glamour, y combinarlo con tonos rojos o burdeos para un contraste sofisticado.",
                      "Para combinar el rosado en tu outfit, puedes utilizarlo como prenda principal y combinarlo con colores neutros en accesorios o prendas complementarias. También puedes crear combinaciones tonales utilizando diferentes tonalidades de rosado, o utilizar estampados que incluyan rosado en su diseño.",
                      "Si quieres resaltar el rosado, puedes combinarlo con colores que contrasten o complementen. Por ejemplo, puedes agregar toques de color con accesorios en tonos verdes o naranjas para crear un contraste llamativo. También puedes combinar el rosado con tonos metálicos como el oro rosado para un aspecto elegante y romántico."]
    },
 
    {
        "tag": "colores_combinan_gris",
        "patterns": ["¿Qué colores combinan bien con el gris?", "¿Cómo puedo combinar el gris en mi outfit?", "¿Qué colores puedo usar para resaltar el gris?", "Combinaciones de colores con gris", "Colores que combinan con gris"],
        "responses": ["El gris es un color neutro y versátil que combina bien con una amplia gama de colores. Algunas opciones para combinar el gris son: combinarlo con tonos pastel como rosa, celeste o lavanda para una combinación suave y delicada, combinarlo con tonos vivos como rojo, amarillo o azul para un contraste audaz, combinarlo con tonos tierra como beige o marrón para una combinación cálida y natural, y combinarlo con tonos metálicos como plateado o dorado para un toque de elegancia.",
                      "Para combinar el gris en tu outfit, puedes utilizarlo como base y combinarlo con colores llamativos para crear un contraste vibrante. También puedes crear combinaciones en blanco y gris para un look elegante y minimalista, o utilizar diferentes tonalidades de gris para un conjunto sofisticado y monocromático.",
                      "Si quieres resaltar el gris, puedes combinarlo con colores que contrasten o complementen. Por ejemplo, puedes agregar toques de color con accesorios en tonos vibrantes como amarillo, verde o rosa para crear un contraste llamativo. También puedes combinar el gris con tonos metálicos como el plata o el oro para un aspecto elegante y sofisticado."]
    },

    {
        "tag": "clima",
        "patterns": ["¿Qué ropa debo usar hoy?", "¿Qué ropa es adecuada para el clima de hoy?", "¿Qué me recomiendas vestir hoy?"],
        "responses": []
    },

    {
        "tag": "recomendación de moda",
        "patterns": ["¿Qué me recomiendas vestir en [ciudad] hoy?", "¿Qué ropa es adecuada para el clima en [ciudad] hoy?"],
        "responses": []
    }
]

vectorizador = TfidfVectorizer()
clasificador = LogisticRegression(random_state=0, max_iter=10000)

etiquetas = []
patrones = []
for intent in intents:
    for patron in intent["patterns"]:
        etiquetas.append(intent["tag"])
        patrones.append(patron)

x = vectorizador.fit_transform(patrones)
y = etiquetas
clasificador.fit(x, y)

def translate_text(text, dest_language):
    translator = Translator(service_urls=['translate.google.com'])
    translated_text = translator.translate(text, dest=dest_language)
    return translated_text.text

def analyze_image(image):
    configure()
    with open("temp_image.jpg", "wb") as f:
        f.write(image.getvalue())

    img = Image.open("temp_image.jpg")
    img.show()

    prompt = f"A continuación encontrarás algunas páginas recomendadas, donde podrás encontrar más ideas en base al outfit seleccionado: https://www.pinterest.com/, https://www.bantoa.com/es/"
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150,
        top_p=1,
        stop=None,
        temperature=0.9,
        frequency_penalty=0,
        presence_penalty=0.6
    )

    if len(response.choices) > 0 and response.choices[0].text is not None:
        return response.choices[0].text.strip()
    else:
        return ""

def recommend_seasonal_styles(dest_language):
    configure()
    current_month = datetime.datetime.now().month
    season = ""

    if 3 <= current_month <= 5:
        season = "primavera"
    elif 6 <= current_month <= 8:
        season = "verano"
    elif 9 <= current_month <= 11:
        season = "otoño"
    else:
        season = "invierno"

    prompt = f"Recomendaciones de estilo para la temporada de {season}:"
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=350,
        top_p=1,
        stop=None,
        temperature=0.9,
        frequency_penalty=0,
        presence_penalty=0.6
    )

    if len(response.choices) > 0 and response.choices[0].text is not None:
        recommendations = response.choices[0].text.strip()
        translated_recommendations = translate_text(recommendations, dest_language)
        return translated_recommendations
    else:
        return ""

def get_daily_weather(city):
    configure()
    weather_key = "5272eabbc0058d86f2ed908c2d8dec2e"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        weather_description = data["weather"][0]["description"]
        return weather_description
    else:
        return "Lo siento, no pude obtener la información del clima para esa ciudad."

def recommend_clothing(weather, dest_language):
    prompt = f"Recomienda prendas adecuadas para vestir en un clima con la siguiente descripción: {weather}."
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150,
        top_p=1,
        stop=None,
        temperature=0.9,
        frequency_penalty=0,
        presence_penalty=0.6
    )

    recommendation = response.choices[0].text.strip() if response.choices else ""
    translated_recommendation = translate_text(recommendation, dest_language)
    return translated_recommendation

def classify_intent(user_input):
    x_input = vectorizador.transform([user_input])
    intent = clasificador.predict(x_input)[0]
    return intent

def modabot(texto_entrada,dest_language):
    texto_entrada = vectorizador.transform([texto_entrada])
    etiqueta = clasificador.predict(texto_entrada)[0]
    translated_response = ""
    for intent in intents:
        if intent ['tag'] == etiqueta:
            respuesta = random.choice(intent['responses'])
            translated_response = translate_text(respuesta, dest_language)
    return translated_response

language_codes = {
    "English": "en",
    "Español": "es",
    "Français": "fr",
    "Deutch": "de",
    "Italiano": "it",
    "日本 (JA)": "ja"
}

st.set_page_config(page_title="ModaBot", page_icon=":eyeglasses:")

st.title("Chatea con ModaBot")

language = st.sidebar.selectbox("Elige tu idioma", ["English", "Español", "Français", "Deutch", "Italiano", "日本 (JA)"])

st.sidebar.header("Cargar imágenes de referencia")
uploaded_images = st.sidebar.file_uploader("Elige una imagen", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

if uploaded_images:
    st.header("Imágenes de referencia")
    for image in uploaded_images:
        st.image(image)
        description = analyze_image(image)
        st.write(f"Descripción de la imagen: {description}")

counter = 0

def principal():
    global counter
    st.header("ModaBot - Chatbot de moda")
    st.write("Bienvenido a ModaBot. Por favor, escriba un mensaje y presione Enter para iniciar la conversación. Sea lo más específico posible, se responde sobre los siguientes temas: Presupuesto, accesorios, zapatos, colores en tendencia, combinación de colores, gafas, abrigos y pantalones.")
    selected_city = st.sidebar.text_input("Ciudad", value="")
    
    if st.button("Mostrar recomendaciones de estilo de temporada"):
        dest_language = language_codes[language]
        seasonal_recommendations = recommend_seasonal_styles(dest_language)
        st.write(seasonal_recommendations)

    if st.button("Mostrar clima diario"):
        dest_language = language_codes[language]
        city = selected_city.lower()
        daily_weather = get_daily_weather(city)
        clothing_recommendation = recommend_clothing(daily_weather, dest_language)
        st.write(f"El clima en {city} hoy es: {daily_weather}")
        st.write(f"Recomendación de ropa adecuada: {clothing_recommendation}")

    counter += 1
    user_input = st.text_input("Escribe aquí tu mensaje", key=f"user_input_{counter}")
 
    if user_input:
        dest_language = language_codes[language]
        respuesta = modabot(user_input, dest_language)
        st.write(respuesta)

        if respuesta.lower() in ['adiós', 'adios', 'chao', 'Gracias', "bye"]:
            st.write("¡Gracias por hablar conmigo! ¡Que tengas un gran día!")
            st.stop()

if __name__ == '__main__':
    principal()