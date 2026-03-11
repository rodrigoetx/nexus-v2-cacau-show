import streamlit as st
import io
import os
import time
import shutil
import re
from pathlib import Path
from PIL import Image, ImageEnhance
from rembg import remove
from PyPDF2 import PdfReader, PdfWriter
from fpdf import FPDF
import pytesseract

# Configuração de Página e UX de HUD
st.set_page_config(page_title="Nexus V2 - Comando", page_icon="⚡", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* Estética Dark Mode HUD */
    .header-style {
        font-family: 'Courier New', Courier, monospace;
        font-size: 3rem;
        font-weight: bold;
        color: #D4AF37; /* Dourado */
        text-align: center;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 2rem;
    }
    .subheader-style {
        color: #8b949e;
        text-align: center;
        margin-bottom: 2rem;
        font-style: italic;
    }
    .stButton>button {
        width: 100%;
        background-color: #1E1E1E;
        color: #D4AF37; /* Dourado */
        border: 1px solid rgba(212, 175, 55, 0.3);
        border-radius: 6px;
        transition: 0.2s;
    }
    .stButton>button:hover {
        background-color: #2A2A2A;
        border-color: #D4AF37;
        color: #ffffff;
    }
    </style>
""", unsafe_allow_html=True)

def show_feedback(msg="Missão Cumprida!"):
    progress_bar = st.progress(0)
    for i in range(100):
        time.sleep(0.01)
        progress_bar.progress(i + 1)
    st.success(f"✔️ {msg}")
    st.balloons()
    
def formatar_documento(doc):
    """Limpa e formata CPF (11 dígitos) ou CNPJ (14 dígitos)."""
    numeros = re.sub(r'\D', '', doc)
    if len(numeros) == 11:
        return f"{numeros[:3]}.{numeros[3:6]}.{numeros[6:9]}-{numeros[9:]}"
    elif len(numeros) == 14:
        return f"{numeros[:2]}.{numeros[2:5]}.{numeros[5:8]}/{numeros[8:12]}-{numeros[12:]}"
    return doc # Retorna como digitado caso não tenha qtde exata de CPF/CNPJ

st.markdown('<div class="header-style">⚡ NEXUS V2 - CENTRAL DE COMANDO</div>', unsafe_allow_html=True)
st.markdown('<div class="subheader-style">Interface Administrativa de Alta Produtividade</div>', unsafe_allow_html=True)

# Abas das ferramentas
tabs = st.tabs([
    "📄 PDF Forge", 
    "🖼️ Visual Studio Lite", 
    "✍️ The Scribe & Summarizer", 
    "📂 Auto-Organizer", 
    "🧾 Autonomia: Gerador de Recibo"
])

# ----------------- PDF FORGE -----------------
with tabs[0]:
    st.subheader("📄 PDF Forge - Edição e Conversão de Documentos")
    pdf_action = st.radio("Selecione a Operação:", ["Mesclar PDFs", "Extrair Páginas", "Adicionar Marca d'Água"], horizontal=True)
    
    if pdf_action == "Mesclar PDFs":
        uploaded_files = st.file_uploader("Upload de PDFs para Mesclar", type="pdf", accept_multiple_files=True)
        if st.button("🔌 Mesclar") and uploaded_files:
            merger = PdfWriter()
            for pdf in uploaded_files:
                merger.append(pdf)
            output = io.BytesIO()
            merger.write(output)
            output.seek(0)
            show_feedback("PDFs Mesclados com Sucesso!")
            st.download_button(label="Baixar PDF Mesclado", data=output, file_name="nexus_merged.pdf", mime="application/pdf")
            
    elif pdf_action == "Extrair Páginas":
        uploaded_pdf = st.file_uploader("Upload de PDF", type="pdf")
        if uploaded_pdf:
            reader = PdfReader(uploaded_pdf)
            total_pages = len(reader.pages)
            page_num = st.number_input("Número da Página (1-indexado)", min_value=1, max_value=total_pages, value=1)
            
            if st.button("✂️ Extrair Página"):
                writer = PdfWriter()
                writer.add_page(reader.pages[page_num - 1])
                output = io.BytesIO()
                writer.write(output)
                output.seek(0)
                show_feedback("Página Extraída!")
                st.download_button(label=f"Baixar Página {page_num}", data=output, file_name=f"nexus_page_{page_num}.pdf", mime="application/pdf")
                
    elif pdf_action == "Adicionar Marca d'Água":
        target_pdf = st.file_uploader("PDF Principal", type="pdf", key="target")
        watermark_pdf = st.file_uploader("PDF contendo apenas a Marca d'Água", type="pdf", key="watermark")
        if st.button("💧 Aplicar Marca d'Água") and target_pdf and watermark_pdf:
            reader_target = PdfReader(target_pdf)
            reader_watermark = PdfReader(watermark_pdf)
            writer = PdfWriter()
            
            watermark_page = reader_watermark.pages[0]
            
            for page in reader_target.pages:
                page.merge_page(watermark_page)
                writer.add_page(page)
                
            output = io.BytesIO()
            writer.write(output)
            output.seek(0)
            show_feedback("Marca d'Água Aplicada!")
            st.download_button(label="Baixar PDF com Marca d'Água", data=output, file_name="nexus_watermarked.pdf", mime="application/pdf")


# ----------------- VISUAL STUDIO LITE -----------------
with tabs[1]:
    st.subheader("🖼️ Visual Studio Lite - Otimização de Imagens")
    img_action = st.radio("Selecione a Operação Visual:", ["Ajustes (Cortar, Rotacionar, Redimensionar)", "✨ Magic Remover (Remover Fundo)"], horizontal=True)
    
    img_file = st.file_uploader("Upload de Imagem", type=["png", "jpg", "jpeg", "webp"])
    
    if img_file:
        image = Image.open(img_file)
        st.image(image, caption="Imagem Original", use_container_width=True)
        
        if img_action == "Ajustes (Cortar, Rotacionar, Redimensionar)":
            col1, col2, col3 = st.columns(3)
            with col1:
                deg = st.slider("Rotação (Graus)", -180, 180, 0)
            with col2:
                width = st.number_input("Nova Largura", value=image.width)
            with col3:
                height = st.number_input("Nova Altura", value=image.height)
                
            if st.button("🔧 Processar Ajustes"):
                processed = image.rotate(-deg, expand=True)
                processed = processed.resize((int(width), int(height)))
                
                output = io.BytesIO()
                processed.save(output, format="PNG")
                output.seek(0)
                
                st.image(processed, caption="Imagem Processada", use_container_width=True)
                show_feedback("Imagens ajustadas prontas para Apresentação!")
                st.download_button(label="Baixar Imagem", data=output, file_name="nexus_adjusted.png", mime="image/png")
                
        elif img_action == "✨ Magic Remover (Remover Fundo)":
            if st.button("✨ Executar Magic Remover"):
                with st.spinner("Processando Inteligência Artificial de Remoção..."):
                    processed = remove(image)
                    output = io.BytesIO()
                    processed.save(output, format="PNG")
                    output.seek(0)
                
                st.image(processed, caption="Fundo Removido", use_container_width=True)
                show_feedback("Fundo Removido com Sucesso!")
                st.download_button(label="Baixar Imagem sem Fundo", data=output, file_name="nexus_nobg.png", mime="image/png")


# ----------------- THE SCRIBE & SUMMARIZER -----------------
with tabs[2]:
    st.subheader("✍️ The Scribe & Summarizer - Automação Textual")
    scribe_action = st.radio("Ferramenta Textual:", ["🔍 OCR (Extrair Texto)", "👔 Transformador de E-mail", "📊 Meeting Summarizer"], horizontal=True)
    
    if scribe_action == "🔍 OCR (Extrair Texto)":
        ocr_file = st.file_uploader("Upload de Foto de Documento (.png, .jpg)", type=["png", "jpg", "jpeg"])
        if st.button("🔍 Extrair Texto via OCR") and ocr_file:
            try:
                img = Image.open(ocr_file)
                text = pytesseract.image_to_string(img)
                if text.strip() == "":
                    text = "[Nenhum texto detectado ou Tesseract não instalado corretamente.]"
                st.text_area("Texto Extraído:", value=text, height=200)
                show_feedback("Extração de Texto (OCR) Concluída!")
            except Exception as e:
                st.error(f"Erro no OCR: Pode ser necessário instalar o tesseract-ocr no sistema. Detalhe: {e}")
                
    elif scribe_action == "👔 Transformador de E-mail":
        st.info("Transforme um rascunho com gírias e informalidades em um e-mail 100% corporativo.")
        raw_email = st.text_area("Rascunho do E-mail (Gírias/Informal)", "Fala chefe, beleza? A parada do projeto deu ruim aqui, mas a gente já tá correndo atrás pra arrumar. Tamo junto.")
        if st.button("👔 Converter para Corporativo"):
            # Mock de processamento NLP (ideal seria via LLM openai/gemini)
            st.divider()
            corporate_email = "Prezado Responsável,\n\nGostaria de informar que identificamos um contratempo em nosso projeto recente. No entanto, nossa equipe já está trabalhando diligentemente nas devidas correções e medidas de mitigação.\n\nFico à disposição para maiores esclarecimentos.\n\nAtenciosamente,\n[Seu Nome]"
            st.text_area("E-mail Formal (Polido):", value=corporate_email, height=200)
            show_feedback("E-mail Polido e Pronto!")
            
    elif scribe_action == "📊 Meeting Summarizer":
        st.info("Cole os apontamentos brutos da reunião para extrair Resumo Executivo e Action Items.")
        meeting_notes = st.text_area("Ata Bruta da Reunião", height=150)
        if st.button("📋 Gerar Resumo Executivo"):
            # Mock de extração NLP (Action Items e Resumo)
            resumo = "Resumo Executivo Simulador (Via Processamento NLP):\n- Discussão sobre alinhamento do projeto atual.\n- Mapeamento de impedimentos técnicos."
            action_items = "- [ ] Marcos: Atualizar cronograma\n- [ ] Equipe Dev: Resolver bloqueios técnicos"
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### 📝 Resumo")
                st.write(resumo)
            with col2:
                st.markdown("### 📌 Action Items")
                st.write(action_items)
            show_feedback("Resumo Gerado com Sucesso!")


# ----------------- AUTO-ORGANIZER -----------------
with tabs[3]:
    st.subheader("📂 Auto-Organizer - Organização Mágica de Arquivos")
    st.write("Varre uma pasta local e organiza os arquivos automaticamente por categoria em subpastas.")
    
    target_dir = st.text_input("Caminho Absoluto da Pasta (ex: /mnt/share/downloads ou ./downloads):")
    
    if st.button("🧹 Organizar Automaticamente"):
        if os.path.exists(target_dir) and os.path.isdir(target_dir):
            categories = {
                "PDFs_Documentos": [".pdf", ".docx", ".doc", ".txt", ".xlsx", ".csv"],
                "Imagens_Fotos": [".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"],
                "Vídeos": [".mp4", ".avi", ".mkv", ".mov"],
                "Áudios": [".mp3", ".wav"],
                "Executáveis": [".exe", ".msi"],
                "Compactados": [".zip", ".rar", ".7z", ".tar", ".gz"]
            }
            
            moved_count = 0
            for filename in os.listdir(target_dir):
                filepath = os.path.join(target_dir, filename)
                if os.path.isfile(filepath):
                    ext = os.path.splitext(filename)[1].lower()
                    for folder, exts in categories.items():
                        if ext in exts:
                            cat_dir = os.path.join(target_dir, folder)
                            os.makedirs(cat_dir, exist_ok=True)
                            shutil.move(filepath, os.path.join(cat_dir, filename))
                            moved_count += 1
                            break
                            
            show_feedback(f"Organização Automática concluída! {moved_count} arquivos organizados nas respectivas subpastas.")
        else:
            st.error("Caminho inválido ou pasta inexistente.")


# ----------------- GERADOR DE RECIBO (AUTONOMIA SÊNIOR) -----------------
with tabs[4]:
    st.subheader("🧾 Autonomia: Gerador de Recibo Oficial")
    st.write("Criação ágil de recibos em PDF com layout de alta qualidade e modelo corporativo.")
    
    with st.form("receipt_form_ceo"):
        col_hdr1, col_hdr2 = st.columns(2)
        with col_hdr1:
            emissor_nome = st.text_input("Empresa Emissora / Profissional", value="TECH STARTUP INC.")
            emissor_doc_raw = st.text_input("CNPJ / CPF do Emissor", value="00000000000100", help="Digite apenas os números, a formatação será automática.")
        with col_hdr2:
            pagador_nome = st.text_input("Cliente Pagador (COBRAR A)", placeholder="Nome do Cliente ou Empresa")
            pagador_doc_raw = st.text_input("Documento do Cliente (Opcional)", help="Digite apenas os números.")
            
        st.divider()
        col1, col2, col3 = st.columns([3, 1, 1.5])
        with col1:
            descricao_servico = st.text_input("Descrição do Serviço / Produto", placeholder="Consultoria Tecnológica")
        with col2:
            quantidade = st.number_input("QTD", min_value=1, step=1, value=1)
        with col3:
            valor_unitario = st.number_input("Preço Unitário (R$)", min_value=0.01, step=50.0, value=1500.00)
            
        st.divider()
        col_ft1, col_ft2 = st.columns(2)
        with col_ft1:
            opcoes_pagamento = ["PIX", "Transferência Bancária (TED/DOC)", "Cartão de Crédito", "Cartão de Débito", "Dinheiro", "Boleto Bancário"]
            forma_pagamento = st.selectbox("Forma de Pagamento", opcoes_pagamento)
            data_recibo = st.date_input("Data de Emissão")
        with col_ft2:
            assinatura_nome = st.text_input("Nome Impresso na Assinatura:", value="Diretoria Financeira")
            
        submitted = st.form_submit_button("🔨 Gerar Recibo Premium (Padrão CEO)")

    if submitted:
        # Formatar documentos antes de gerar o PDF
        emissor_doc = formatar_documento(emissor_doc_raw)
        pagador_doc = formatar_documento(pagador_doc_raw) if pagador_doc_raw else ""
        
        valor_total = quantidade * valor_unitario
        pdf = FPDF()
        pdf.add_page()
        
        # Cores e Fontes Globais
        GREY_DARK = (40, 40, 40)
        GREY_LIGHT = (240, 240, 240)
        THEME_COLOR = (44, 62, 80) # Azul Escuro Corporativo
        
        # --- HEADER ---
        # Título "recibo" minimalista
        pdf.set_font("Arial", 'B', 32)
        pdf.set_text_color(*GREY_DARK)
        pdf.cell(100, 15, txt="recibo", ln=0, align='L')
        
        # Logo placeholder minimalista circular/badged (lado direito)
        pdf.set_fill_color(*THEME_COLOR)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", 'B', 14)
        pdf.set_xy(160, 10)
        pdf.cell(40, 15, txt="LOGO", border=0, ln=1, align='C', fill=True)
        
        pdf.ln(10)
        
        # --- INFOS DA EMPRESA (DE) ---
        pdf.set_text_color(*GREY_DARK)
        # Lado Esquerdo (DE) e Lado Direito (Detalhes Fiscais)
        pdf.set_y(35)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(100, 6, txt="DE (EMISSOR)", border=0, ln=0, align='L')
        
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(50, 6, txt="RECIBO #", border=0, ln=0, align='R')
        pdf.set_font("Arial", '', 10)
        pdf.cell(40, 6, txt=f"NXV2-{int(time.time() % 10000):04d}", border=0, ln=1, align='R')
        
        pdf.set_font("Arial", '', 10)
        pdf.cell(100, 5, txt=str(emissor_nome).upper(), border=0, ln=0, align='L')
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(50, 5, txt="DATA DO RECIBO", border=0, ln=0, align='R')
        pdf.set_font("Arial", '', 10)
        pdf.cell(40, 5, txt=data_recibo.strftime("%d/%m/%Y"), border=0, ln=1, align='R')
        
        pdf.cell(100, 5, txt=f"DOC: {emissor_doc}", border=0, ln=1, align='L')
        pdf.ln(10)
        
        # --- CLIENTE (COBRAR A) ---
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(0, 6, txt="COBRAR A (CLIENTE)", ln=1)
        pdf.set_font("Arial", '', 10)
        pdf.cell(0, 5, txt=str(pagador_nome).upper(), ln=1)
        if pagador_doc:
            pdf.cell(0, 5, txt=f"DOC: {pagador_doc}", ln=1)
        
        pdf.ln(15)
        
        # --- TABELA DE ITENS (HEADER DE TABELA) ---
        pdf.set_fill_color(245, 245, 245)
        pdf.set_draw_color(200, 200, 200)
        pdf.set_line_width(0.3)
        pdf.set_font("Arial", 'B', 10)
        
        # Cabeçalhos com fundo cinza e borda superior/inferior
        pdf.cell(15, 10, txt="QTD", border='TB', align='C', fill=True)
        pdf.cell(110, 10, txt="DESCRIÇÃO", border='TB', align='L', fill=True)
        pdf.cell(35, 10, txt="PREÇO UN.", border='TB', align='R', fill=True)
        pdf.cell(30, 10, txt="VALOR", border='TB', align='R', fill=True)
        pdf.ln(10)
        
        # Corpo da Tabela
        pdf.set_font("Arial", '', 10)
        pdf.cell(15, 10, txt=str(quantidade), border='B', align='C')
        pdf.cell(110, 10, txt=str(descricao_servico), border='B', align='L')
        pdf.cell(35, 10, txt=f"{valor_unitario:,.2f}", border='B', align='R')
        pdf.cell(30, 10, txt=f"{valor_total:,.2f}", border='B', align='R')
        pdf.ln(15)
        
        # --- TOTAIS ---
        pdf.set_font("Arial", '', 10)
        pdf.cell(130, 6, txt="", border=0) # Espaço
        pdf.cell(30, 6, txt="Subtotal", border=0, align='R')
        pdf.cell(30, 6, txt=f"{valor_total:,.2f}", border=0, align='R')
        pdf.ln(10)
        
        # Caixa de TOTAL
        pdf.set_font("Arial", 'B', 16)
        pdf.set_draw_color(0, 0, 0)
        pdf.set_line_width(0.6)
        
        pdf.cell(130, 15, txt="TOTAL", border='TLB', align='L')
        pdf.cell(60, 15, txt=f"R$ {valor_total:,.2f}", border='TRB', align='R')
        pdf.ln(30)
        
        # --- ASSINATURA E TERMOS ---
        # Lado Esquerdo: Termos
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(100, 6, txt="TERMOS E CONDIÇÕES", ln=1)
        pdf.set_font("Arial", '', 9)
        pdf.cell(100, 5, txt="O pagamento declara quitação sobre o serviço ou produto apontado.", ln=1)
        pdf.cell(100, 5, txt=f"Forma de Pagamento: {forma_pagamento}", ln=1)
        
        # Lado Direito: Assinatura
        # Volta o cursor Y para desenhar assinatura
        current_y = pdf.get_y()
        pdf.set_y(current_y - 25)
        pdf.set_x(120)
        
        # Assinatura manuscrita simulada / Estilizada
        pdf.set_font("Arial", 'I', 20) # Fonte itálico simulando assinatura
        pdf.set_text_color(*THEME_COLOR)
        pdf.cell(70, 15, txt=str(assinatura_nome).title(), align='C', ln=1)
        
        pdf.set_x(120)
        pdf.set_draw_color(*GREY_DARK)
        pdf.set_line_width(0.2)
        pdf.line(130, pdf.get_y(), 180, pdf.get_y()) # Risquinho da assinatura
        pdf.set_font("Arial", 'I', 8)
        pdf.set_text_color(150, 150, 150)
        pdf.cell(70, 5, txt="Assinatura Digital / Responsável", align='C', ln=1)
        
        pdf.set_y(280)
        pdf.cell(0, 5, txt="Documento emitido de forma automatizada por Nexus V2 Command Center.", align='C')
        
        output = pdf.output(dest='S').encode('latin1')
        st.download_button(label="📥 Download Recibo Nível CEO", data=output, file_name="Recibo_Premium_CEO.pdf", mime="application/pdf")
        show_feedback("Design de Alto Padrão Aplicado. Recibo Pronto!")



# ----------------- RODAPÉ / COPYRIGHT -----------------
st.sidebar.markdown(
    """
    <div style='position: fixed; bottom: 20px; width: 100%; color: #666; font-size: 0.8rem; line-height: 1.4em;'>
        Nexus OS v2.5<br>
        System Architect: <b>Rodrigo Espinosa</b><br>
        Co-authored by Neural Intelligence 2026
    </div>
    """,
    unsafe_allow_html=True
)

