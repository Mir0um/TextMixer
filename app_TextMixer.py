import json
import os
import streamlit as st
from Traduction import translate
import base64
from text_to_speech import text_to_audio as TTS
import time
import datetime


with open('config.json', 'r', encoding='utf-8') as file:
    config = json.load(file)

text_app = config["text_app"]
text_ifo = config["text_ifo"]
lang = config["lang"]

def sec_to_min_sec(seconds):
    if seconds < 60:
        return (f":green[{round(seconds,2)}] secondes")
    else:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return (f":green[{round(minutes)}] minutes et :green[{round(remaining_seconds,2)}] secondes")

def audio_player(audio_file):
    audio_bytes = open(audio_file, "rb").read()
    encoded_audio = base64.b64encode(audio_bytes).decode()
    st.markdown(f'<audio controls autoplay src="data:audio/mp3;base64,{encoded_audio}" > </audio>', unsafe_allow_html=True)

def transformations(user_text,mod):
    user_text_old =user_text
    now = datetime.datetime.now()
    formatted_date_time = now.strftime("%d/%m/%Y %H:%M:%S")

    start_time = time.time()
    print("\n\n" + formatted_date_time+ "=" * 20)

    if mod != "Mode normal.":
        histo = {}
        histo["start"] = {}
        histo["start"]["time"] = time.time() - start_time
        histo["start"]["fr"] = user_text
        histo["start"]["len"] = len(histo["start"]["fr"])

    old_lang = "fr"
    progress_bar = st.progress(0)
    progress_bar.progress(0, text="0.00%")  # text="Cela peut prendre quelques minutes.")

    for count, i in enumerate(list(lang.keys())):

        user_text = translate(user_text, i, old_lang)

        progress = 100 - (((len(list(lang.keys())) - count) / len(list(lang.keys()))) * 100 )
        #print(formatted_date_time,round(progress,3),'%', end="\r")
        promt = str(round(progress,2)) +"%"
        progress_bar.progress(round(progress),text=promt ) #text="Cela peut prendre quelques minutes.")


        if mod != "Mode normal.":
            histo[lang[i]] = {}
            histo[lang[i]]["id"] = i
            histo[lang[i]]["old_lang"] = old_lang
            histo[lang[i]]["time"] = time.time() - start_time
            histo[lang[i]]["text"] = user_text
            histo[lang[i]]["french"] = translate(user_text, "fr")
            histo[lang[i]]["len"] = len(histo[lang[i]]["french"])
        old_lang = i

    user_text = translate(user_text, "fr")

    st.success('Traitement terminé!')
    st.header("resulta:")

    audio_file = TTS(user_text, "fr")
    audio_player(audio_file)
    os.remove(audio_file)

    st.write(str(user_text))


    st.write("---")
    if mod != "Mode normal.":

        end_time = time.time()
        histo["time"] = {}
        histo["time"]["start"] = start_time
        histo["time"]["end"] = end_time
        histo["time"]["total"] = end_time - start_time

        st.write("Statistique de la transformation:",histo)
        st.write("---")

    st.write("Temps de traitement :",sec_to_min_sec(time.time() - start_time),"s")
    progress_bar.progress(100)

    with open("Log.json", "a", encoding='utf-8') as fichier:
        log = {}
        log["start_time"] = formatted_date_time
        log["mod"] = mod
        log["input"] = user_text_old
        log["output"] = user_text
        log["Executing_time"] = time.time() - start_time
        json_log = json.dumps(log)
        fichier.write(str(json_log)+"\n")


def app():
    st.write(text_app["head"])

    user_text = st.text_area("Entrez votre texte ici:", height=350, help=text_app["help"])

    mod = st.radio("Voulez-vous utiliser le mode statistique:", ["Mode normal.", "Mode Statistique."])

    if mod != "Mode normal.":
        st.error("Attention, le mode Statistique et activé, le temps de traitement sera plus long.")


    if st.button("Transformer mon texte."):
        if not any(char.isalpha() or char.isdigit() for char in user_text):
            st.error("Vous devez entrer un texte")
        else:
            with st.spinner('Transformation en cours...'):
                transformations(user_text, mod)


def info():
    st.title("info")
    st.write(text_ifo["temp"])

def main():
    st.header(text_app["title"])

    pages = {
        "Application ": app,
        "info": info,
    }

    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("Aller à", list(pages.keys()))

    pages[selection]()

    st.write("---")
    st.write(text_app["Contact"])

if __name__ == "__main__":
    main()