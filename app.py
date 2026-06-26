import re
from io import BytesIO
from gtts import gTTS
import base64
import os
import streamlit as st
from google import genai
from google.genai import types
SECILEN_RESIM = "arkaplan.png"
API_KEY = ""
# --- 2. SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Evrensel Dil İrlümAI", page_icon="🌍", layout="centered")
SECILEN_RESIM = "arkaplan.png"
# --- 1. SAYFA YAPILANDIRMASI (Geniş Mod ve İkon) ---
st.set_page_config(page_title="Evrensel Dil İrlümAI", page_icon="🌍", layout="centered")
bg_resim_css = ""
if os.path.exists(SECILEN_RESIM):
    with open(SECILEN_RESIM, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    
    bg_resim_css = f"""
    #root, [data-testid="stAppViewContainer"], .stApp {{
        background: linear-gradient(rgba(20, 140, 140, 0.85), rgba(15, 115, 115, 0.88)), url(data:image/png;base64,{encoded_string}) !important;
        background-size: cover !important;
        background-attachment: fixed !important;
    }}
    """
else:
    bg_resim_css = """
    #root, [data-testid="stAppViewContainer"], .stApp {
        background-color: #148c8c !important; 
    }
    """

# --- NÜKLEER CSS (Alttaki Siyah Şeridi Kazıma Operasyonu) ---
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;1,600&display=swap');

    {bg_resim_css}

    /* 1. Üst Bar Şeffaf */
    header[data-testid="stHeader"] {{
        background: transparent !important;
    }}

    /* 2. ALTTAKI SİYAH BARI YOK EDEN 'AĞIR SİLAH' KOMBO SEÇİCİ */
    [data-testid="stBottom"], 
    [data-testid="stBottom"] > *,
    [data-testid="stBottomBlockContainer"],
    div[data-testid^="stBottom"],
    .stAppBottom,
    .stAppBottom > *,
    section[data-testid="stAppViewContainer"] > div:last-child,
    div:has(> [data-testid="stChatInput"]),
    div:has(> div > [data-testid="stChatInput"]),
    footer {{
        background: transparent !important;
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }}

    /* 3. Mesaj Yazma Kapsülünün Kendisi (Havada süzülen Koyu Turkuaz Cam) */
    [data-testid="stChatInputContainer"] {{
        background-color: rgba(10, 75, 75, 0.75) !important; /* Arka planla dikişsiz uysun diye Koyu Turkuaz */
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(255, 255, 255, 0.4) !important;
        border-radius: 25px !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3) !important;
    }}

    /* İçine yazılan yazılar Saf Beyaz */
    [data-testid="stChatInputContainer"] textarea {{
        color: #ffffff !important;
    }}
    [data-testid="stChatInputContainer"] textarea::placeholder {{
        color: rgba(255, 255, 255, 0.6) !important;
    }}

    /* Yazılar ve Balonlar */
    h1, h2, h3 {{
        font-family: 'Playfair Display', serif !important;
        font-style: italic !important;
        color: #ffffff !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }}

    [data-testid="stChatMessageContent"] {{
        background-color: rgba(135, 206, 235, 0.90) !important;
        color: #002b2b !important;
        border-radius: 15px;
        padding: 10px 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.15);
    }}

    .stChatMessage {{padding: 0.5rem 1rem !important;}}
    .stButton {{margin-top: 20px;}}
</style>
""", unsafe_allow_html=True)

# --- 2. GİZLİ CSS MAKYAJI (Boşlukları Daraltma) ---
st.markdown("""
<style>
    /* Mesaj kutularının altındaki gereksiz dev boşluğu törpülüyoruz */
    .stChatMessage {padding: 0.5rem 1rem !important;}
    /* Butonun üstündeki boşluğu açalım */
    .stButton {margin-top: 20px;}
</style>
""", unsafe_allow_html=True)

# --- 3. SOL KONTROL PANELİ (SIDEBAR) ---
with st.sidebar:
    st.header("🌍 Evrensel Dil İrlümAI")
    st.caption("Yapay Zeka Destekli Dil Asistanı")
    st.divider() # Araya şık bir çizgi
    
    st.info("💡 **Nasıl Çalışır?**\nAşağıdaki kutuya hangi dilde 'Merhaba' yazarsanız, sistem anında o dilin hocasına dönüşür.")
    
    st.divider()
    
    # SOHBETİ SIFIRLAMA BUTONU (İstediğin buton!)
    if st.button("🔄 Yeni Derse Başla", type="primary", use_container_width=True):
        st.session_state.messages = [] # Ekrandaki yazıları sil
        if "chat_session" in st.session_state:
            del st.session_state.chat_session # Arka plandaki sohbet hafızasını öldür
        st.rerun() # Sayfayı taptaze yenile!


# --- 4. ANA EKRAN BAŞLIĞI ---
st.title("🌍 AI Dil")
st.caption("Sen hangi dili konuşursan, ben o dilin ustasıyım.")

# --- 5. YAPAY ZEKA AYARLARI ---
# --- 5. YAPAY ZEKA AYARLARI ---

# 1. ŞALTER: Sadece ilk açılışta çalışır, Google motorunu kasaya koyar
if "client" not in st.session_state:
    st.session_state.client = genai.Client(api_key=API_KEY)

# 2. ŞALTER: Hem ilk açılışta HEM DE 'Yeni Derse Başla' dendiğinde çalışır!
if "chat_session" not in st.session_state:
    
    # --- 3. ÖĞRETMEN YASALARI ---
    ogretmen_talimati = """
    
Sen dünyadaki tüm dilleri ana dili gibi konuşabilen efsanevi bir dil öğretmenisin. 
SANA KOYDUĞUM ÇOK KATI KURAL (Okunuş ve Alfabe Kuralı):
Öğrenciye yabancı dilde kelime yazdığında, cevabını İSTİSNASIZ şu 3'lü şablona göre vereceksin:
ÇOK ÖNEMLİ FONETİK KURALI:
[Türkçe Okunuşu] kısmını yazarken kelimeleri tek tek değil, o dilin doğal konuşma akışına göre yaz. Özellikle Fransızca gibi dillerde ulama (Liaison) varsa harfleri birbirine bağla. 
Örn: "Comment allez-vous?" cümlesini [Koman ale vu] olarak değil, fonetik olarak tam duyulduğu gibi [Komantalevu] şeklinde yaz.

• Orijinal Yazılışı
• [Türkçe Okunuşu]
• (Türkçe Anlamı)


SANA KOYDUĞUM ÇOK KRİTİK GİZLİ KOD KURALI:
Her cevabının EN ÜST SATIRINA, bilgisayarın okuması için şu etiketi kesinlikle ekleyeceksin:
[TTS:dilin_2_harfli_kodu:sadece_yabanci_dildeki_cümleler]

Örnekler:
Fransızca için -> [TTS:fr:Bonjour comment allez-vous ?]
Rusça için -> [TTS:ru:Привет, как дела?]

Bu etiketin içine ASLA Türkçe kelime, okunuş veya anlam koyma. Sadece saf yabancı dil olsun.


Kuralların:
1. Asla İngilizce açıklama ekleme.
2. Asla "Şunu da açıklarım" gibi ekstra cümleler kurma.
3. Sadece ve sadece istediğim formatta yaz. Formatın dışına çıkan her karakter için cezalandırılırsın.
4. İlk mesajda hangi dilde yazarsa o dilin öğretmeni ol.
5. Dili kilitledikten sonra kural değişmez: Hataları nazikçe açıkla, doğruysa tebrik et.
6. Sohbetin devamı için cevabın sonunda o dilde basit, A1-A2 seviyesinde tek bir soru sor.
7.Sohbetin sonunda sorduğun sorunun okunuşunu ve anlamını da kesinlikle ekle.
8. Cevapların bir öğretmen gibi kısa, net ve cesaretlendirici olsun.
"""

    
    yapilandirma = types.GenerateContentConfig(
        system_instruction=ogretmen_talimati,
        temperature=0.7,
    )
    
    st.session_state.chat_session = st.session_state.client.chats.create(model="gemini-1.5-flash-latest", config=yapilandirma)
    st.session_state.messages = []

# --- 6. GEÇMİŞ MESAJLARI EKRANA ÇİZME ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "audio" in msg and msg["audio"]:
            st.audio(msg["audio"], format="audio/mp3")

# --- 7. KULLANICI GİRDİSİ VE CEVAP DÖNGÜSÜ ---
kullanici_girdisi = None

if "secilen_vitrin_senaryosu" in st.session_state:
    kullanici_girdisi = st.session_state.secilen_vitrin_senaryosu
    del st.session_state.secilen_vitrin_senaryosu # Tekrar tetiklenmesin diye hafızadan sil
else:
    kullanici_girdisi = st.chat_input("Bir dilde bir şeyler yaz...")

if kullanici_girdisi:
    with st.chat_message("user", avatar="👤"):
        st.markdown(kullanici_girdisi)
    st.session_state.messages.append({"role": "user", "content": kullanici_girdisi})
    
    with st.chat_message("assistant", avatar="🧑‍🏫"):
        with st.spinner("Hoca düşünüyor ve sesini akort ediyor..."):
            cevap = st.session_state.chat_session.send_message(kullanici_girdisi)
            ham_metin = cevap.text
            
            # --- 3. ASİSTAN HÜCRESİ: SES AYIKLAMA VE ÜRETME MOTORU ---
            ses_verisi = None
            gosterilecek_metin = ham_metin
            
            # Regex ile gizli [TTS:dil:metin] etiketini yakalıyoruz
            match = re.search(r"\[TTS:\s*([a-zA-Z]{2,3})\s*:(.*?)\]", ham_metin)
            if match:
                dil_kodu = match.group(1).lower().strip()
                okunacak_saf_metin = match.group(2).strip()
                
                # Çirkin gizli etiketi ekrandaki metinden siliyoruz
                gosterilecek_metin = re.sub(r"\[TTS:.*?\]\n*", "", ham_metin).strip()
                
                # Google TTS motorunu hafızada ateşle
                try:
                    tts = gTTS(text=okunacak_saf_metin, lang=dil_kodu, slow=False)
                    fp = BytesIO()
                    tts.write_to_fp(fp)
                    fp.seek(0)
                    ses_verisi = fp.getvalue()
                except Exception as e:
                    st.caption(f"⚠️ Ses motoru başlatılamadı: {e}")

            # --- EKRANA BASMA VE SESİ OYNATMA ---
            st.markdown(gosterilecek_metin)
            if ses_verisi:
                st.audio(ses_verisi, format="audio/mp3")
            
    # Hafızaya eklerken artık 'cevap.text' değil, temizlenmiş metni ve sesi ekliyoruz
    st.session_state.messages.append({
        "role": "assistant", 
        "content": gosterilecek_metin,
        "audio": ses_verisi
    })
    st.rerun() # Vitrindeki butonları "anında" yok etmek için sayfayı tazele!
