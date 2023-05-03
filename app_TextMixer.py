import streamlit as st
from gtts import gTTS
import datetime
import requests
import tempfile
import base64
import json
import time
import uuid
import os


def generate_uuid():
    return uuid.uuid4()


with open('config.json', 'r', encoding='utf-8') as file:
    config = json.load(file)

text_app = config["text_app"]
text_ifo = config["text_ifo"]
lang = config["lang"]


def sec_to_min_sec(seconds):
    if seconds < 60:
        return f":green[{round(seconds, 2)}] secondes"
    else:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f":green[{round(minutes)}] minutes et :green[{round(remaining_seconds, 2)}] secondes"


def text_to_audio(text, lang):
    tts = gTTS(text, lang=lang)
    with tempfile.NamedTemporaryFile(delete=False) as fp:
        temp_file = fp.name
    tts.save(temp_file)
    return temp_file


def audio_player(audio_file):
    audio_bytes = open(audio_file, "rb").read()
    encoded_audio = base64.b64encode(audio_bytes).decode()
    st.markdown(f'<audio controls autoplay src="data:audio/mp3;base64,{encoded_audio}" > </audio>',
                unsafe_allow_html=True)


def translate(text, target_language, source=None):
    if source is None:
        source = "auto"

    url = 'https://translate.googleapis.com/translate_a/single'
    params = {
        'client': 'gtx',
        'sl': source,
        'tl': target_language,
        'dt': 't',
        'q': text
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        translated_text = ""
        for sentence in response.json()[0]:
            translated_text += sentence[0]
        return translated_text
    else:
        return None


def transformations(user_text, mod):
    user_text_old = user_text
    now = datetime.datetime.now()
    formatted_date_time = now.strftime("%d/%m/%Y %H:%M:%S")

    start_time = time.time()
    print(formatted_date_time, [mod[5:11]], (user_text if len(user_text) <= 50 else user_text[:50] + "..."))

    if mod != "Mode normal.":
        histo = {"start": {}}
        histo["start"]["time"] = time.time() - start_time
        histo["start"]["fr"] = user_text
        histo["start"]["len"] = len(histo["start"]["fr"])

    old_lang = "fr"
    progress_bar = st.progress(0)
    progress_bar.progress(0, text="0.00%")

    for count, i in enumerate(list(lang.keys())):
        
        user_text = translate(user_text, i, old_lang)

        progress = 100 - (((len(list(lang.keys())) - count) / len(list(lang.keys()))) * 100)
        # print(formatted_date_time,round(progress,3),'%', end="\r")
        promt = str(round(progress, 2)) + "%"
        progress_bar.progress(round(progress), text=promt)

        if mod != "Mode normal.":
            histo[lang[i]] = {}
            histo[lang[i]]["id"] = i
            histo[lang[i]]["old_lang"] = old_lang
            histo[lang[i]]["time"] = time.time() - start_time
            histo[lang[i]]["text"] = user_text
            histo[lang[i]]["french"] = translate(user_text, "fr")
            histo[lang[i]]["len"] = len(histo[lang[i]]["french"])
        old_lang = i

    st.balloons()

    user_text = translate(user_text, "fr")

    st.success('Traitement terminé!')
    st.header("resulta:")

    audio_file = text_to_audio(user_text, "fr")
    st.audio(audio_file,format="audio/wav")
    st.text(audio_file) #dev
    os.remove(audio_file)
    st.balloons()

    st.write(str(user_text))

    st.write("---")
    if mod != "Mode normal.":
        end_time = time.time()
        histo["time"] = {}
        histo["time"]["start"] = start_time
        histo["time"]["end"] = end_time
        histo["time"]["total"] = end_time - start_time

        st.write("Statistique de la transformation:")
        st.json(histo)
        st.write("---")

    st.write("Temps de traitement :", sec_to_min_sec(time.time() - start_time), "s")
    progress_bar.progress(100)

    with open("Log.json", "a", encoding='utf-8') as fichier:
        log = {}
        log["uuid"] = uuid
        log["start_time"] = formatted_date_time
        log["mod"] = mod[5:11]
        log["input"] = user_text_old
        log["output"] = user_text
        log["Executing_time"] = time.time() - start_time
        json_log = json.dumps(log)
        fichier.write(str(json_log) + "\n")


def app():
    st.write(text_app["head"])

    user_text = st.text_area("Entrez votre texte ici:", height=350, help=text_app["help"])

    st.write("Voulez-vous utiliser le mode statistique:")
    mod = st.checkbox('Mode Statistique.', )

    if mod:
        st.warning("Attention, le mode Statistique et activé, le temps de traitement sera plus long.", icon="⚠️")
        mod = "Mode statistique."
    else:
        mod = "Mode normal."

    if st.button("Transformer mon texte."):
        if not any(char.isalpha() or char.isdigit() for char in user_text):
            st.info("Vous devez entrer un texte", icon="ℹ️")
        else:
            with st.spinner('Transformation en cours...'):
                uuid = generate_uuid()
                try:
                    transformations(user_text, mod)
                except Exception as error:
                    erreur = {}
                    erreur["erreur"] = {}
                    erreur["erreur"]["uuid"] = str(uuid)
                    erreur["erreur"]["text"] = user_text
                    erreur["erreur"]["mode"] = mod
                    erreur["erreur"]["erre"] = str(error)
                    st.write(erreur)
                    with open("error_lod.json", "a", encoding='utf-8') as fichier:

                        fichier.write(str(erreur) + "\n")

                    st.error(f"Une erreur s'est produite nous nous excusons Pour la gêne occasionnée voici votre code erreur: \":blue[{error}]\" et votre identifiant du suivi: \":blue[{uuid}]\" ",icon="🚨")
                    st.write(f"Le code derrière indique le problème rencontré et l'identifiant du suivi indique le code donnez à votre erreur si vous souhaitez en savoir Transmettez l'identifiant de suivi.")

def info():
    st.title("info")
    st.write(text_ifo["temp"])


def test():
    st.write("test")
    st.help(st.write("c la m****"))


def main():
    st.header(text_app["title"])

    pages = {
        "Application ": app,
        "info": info
    }

    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("Aller à", list(pages.keys()))

    pages[selection]()

    st.write("---")
    st.write(text_app["Contact"])


if __name__ == "__main__":
    st.set_page_config(page_title="TextMixer-dev", page_icon="https://jp-sartoris.online/img/logoJP%20blanck.ico")
    main()
