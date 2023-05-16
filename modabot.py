import os
import nltk
import ssl
import streamlit as st
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from googletrans import Translator
import openai
import requests
from PIL import Image
from io import BytesIO

openai.api_key = "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"

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
    with open("temp_image.jpg", "wb") as f:
        f.write(image.getvalue())

    img = Image.open("temp_image.jpg")
    img.show()

    prompt = f"A continuación encontraras algunas páginas recomendadas, donde podras encontrar más ideas en base al outfit seleccionado: https://www.pinterest.com/, https://www.bantoa.com/es/"
    response = openai.Completion.create(
        engine="davinci",
        prompt=prompt,
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.5,
    )

    description = response.choices[0].text.strip()

    os.remove("temp_image.jpg")

    return description


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

st.title("Chatea con Modabot")

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
    st.header("Modabot - Chatbot de moda")
    st.write("Bienvenido al Modabot. Por favor, escriba un mensaje y presione Enter para iniciar la conversación. Sea lo más específico posible, se responde sobre los siguientes temas: Presupuesto, accesorios, zapatos, colores.")
    
    counter += 1
    user_input = st.text_input("Escribe aquí tu mensaje", key=f"user_input_{counter}")
 
    if user_input:
        dest_language = language_codes [language]
        respuesta = modabot(user_input, dest_language)
        st.write(respuesta)

        if respuesta.lower() in ['adiós', 'adios', 'chao', 'Gracias', "bye"]:
            st.write("¡Gracias por hablar conmigo! ¡Que tengas un gran día!")
            st.stop()

if __name__ == '__main__':
    principal()