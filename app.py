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
    /* Estética Dark Mode HUD (Cacau Show Elite Edition) */
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
        background-color: #3D1E16; /* Marrom Cacau */
        color: #D4AF37; /* Dourado */
        border: 1px solid rgba(212, 175, 55, 0.3);
        border-radius: 6px;
        transition: 0.2s;
    }
    .stButton>button:hover {
        background-color: #4b2c21;
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
    "🧾 Autonomia: Gerador de Recibo",
    "🍫 Módulo Cacau Show"
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

# ----------------- MÓDULO CACAU SHOW -----------------
with tabs[5]:
    st.subheader("🍫 Módulo Cacau Show - Operações de Franquia")
    
    cacau_tool = st.radio("Selecione a Ferramenta Operacional:", 
                          ["📂 Auditor de Documentação (Lojas)", "💰 Simulador de Metas", "🏷️ Gerador de Etiquetas de Vitrine", "🛡️ Monitor de Validade", "📅 Gerador de Escala (6x1)"], 
                          horizontal=True)
                          
    if cacau_tool == "📂 Auditor de Documentação (Lojas)":
        st.markdown("### 🔎 Auditoria Expressa - Controle de Rede")
        st.write("Verifique rapidamente quais lojas não possuem um documento obrigatório.")
        
        dir_lojas = st.text_input("Caminho absoluto da pasta raiz de Lojas (ex: /app/rede_lojas ou ./lojas):")
        arquivo_alvo = st.text_input("Nome do arquivo obrigatório a auditar (ex: fechamento.pdf, alvara.pdf):")
        
        if st.button("🚀 Iniciar Varredura de Auditoria"):
            if not dir_lojas or not arquivo_alvo:
                st.warning("Preencha o caminho da pasta e o nome do arquivo para iniciar.")
            elif not os.path.exists(dir_lojas) or not os.path.isdir(dir_lojas):
                st.error("Caminho da rede inválido ou inexistente confira o endereço colado.")
            else:
                lojas_irregulares = []
                for nome_pasta in os.listdir(dir_lojas):
                    caminho_pasta_loja = os.path.join(dir_lojas, nome_pasta)
                    if os.path.isdir(caminho_pasta_loja):
                        caminho_arquivo = os.path.join(caminho_pasta_loja, arquivo_alvo)
                        if not os.path.exists(caminho_arquivo):
                            lojas_irregulares.append(nome_pasta)
                
                if not lojas_irregulares:
                    st.success("Tudo em conformidade! Todas as pastas de lojas possuem o documento exigido.")
                    show_feedback("Auditoria Livre de Pendências")
                else:
                    st.error("⚠️ Irregularidades Detectadas! As seguintes lojas não possuem o arquivo exigido:")
                    for loja in lojas_irregulares:
                        st.markdown(f"- **{loja}**")
                    show_feedback("Auditoria Concluída com Alertas")

    elif cacau_tool == "💰 Simulador de Metas":
        st.markdown("### 📉 Simulador de Resultados e Comissionamento")
        st.write("Calcule rapidamente o atingimento de cotas e provisione o pagamento de bonificações.")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            meta_loja = st.number_input("Meta da Loja (R$)", min_value=0.0, value=50000.0, step=1000.0)
        with col2:
            valor_vendido = st.number_input("Valor Vendido (R$)", min_value=0.0, value=48000.0, step=1000.0)
        with col3:
            comissao_pct = st.number_input("% Comissão Final", min_value=0.0, max_value=100.0, value=2.5, step=0.5)
            
        if st.button("📊 Processar Resultado"):
            st.divider()
            
            # Lógica de cálculo
            if meta_loja > 0:
                atingimento = (valor_vendido / meta_loja)
            else:
                atingimento = 0
                
            valor_comissao = valor_vendido * (comissao_pct / 100)
            
            st.markdown(f"#### Atingimento Mensal: {atingimento * 100:.1f}%")
            
            # Barra de progresso visual (HTML custom)
            color = "#2ea043" if atingimento >= 1.0 else "#da3633" # Verde sucesso, Vermelho falha
            width_pct = min(atingimento * 100, 100)
            
            st.markdown(f"""
                <div style="width: 100%; background-color: #21262d; border-radius: 8px; margin-bottom: 20px;">
                    <div style="width: {width_pct}%; background-color: {color}; height: 24px; border-radius: 8px; transition: width 0.5s;"></div>
                </div>
            """, unsafe_allow_html=True)
            
            col_res1, col_res2 = st.columns(2)
            if atingimento >= 1.0:
                col_res1.success("META ATINGIDA COM SUCESSO! 🎯")
            else:
                falta = meta_loja - valor_vendido
                col_res1.error(f"META NÃO ATINGIDA. Falta R$ {falta:,.2f} para alcançar a cota mínima.")
                
            col_res2.info(f"💰 Comissão Calculada: R$ {valor_comissao:,.2f}")
            show_feedback("Cálculo e Simulação Concluídos")

    elif cacau_tool == "🏷️ Gerador de Etiquetas de Vitrine":
        st.markdown("### 🖨️ Shelf Tags - Impressão de Ofertas e Preços")
        st.write("Gere planilhas em PDF prontas para impressão nas vitrines das lojas, com máxima legibilidade.")
        
        with st.form("tag_form"):
            produto_nome = st.text_input("Nome do Produto", value="Trufa La Creme")
            
            col_preco1, col_preco2 = st.columns(2)
            with col_preco1:
                preco_de = st.number_input("Preço 'De' (R$)", min_value=0.0, value=3.50, step=0.10)
            with col_preco2:
                preco_por = st.number_input("Preço 'Por' (R$) - OBRIGATÓRIO", min_value=0.0, value=2.90, step=0.10)
                
            qtd_etiquetas = st.number_input("Quantidade de Cópias (Etiquetas no PDF)", min_value=1, max_value=24, value=8)
            
            submit_tag = st.form_submit_button("🍫 Gerar Folha Master de Etiquetas (PDF)")
            
        if submit_tag:
            pdf = FPDF()
            pdf.add_page("L") # Paisagem
            
            # Cores Marca - Tom Avermelhado/Marrom escuro
            DARK_CHOC = (60, 20, 20)
            RED_PROMO = (220, 40, 40)
            
            # Definição de grade 4 colunas x 3 linhas
            cols = 4
            tag_w = 65
            tag_h = 55
            margin_x = 15
            margin_y = 15
            
            count = 0
            
            while count < qtd_etiquetas:
                if count > 0 and count % 12 == 0:
                    pdf.add_page("L")
                    
                pos_in_page = count % 12
                row = pos_in_page // cols
                col = pos_in_page % cols
                
                x = margin_x + (col * (tag_w + 5))
                y = margin_y + (row * (tag_h + 5))
                
                # Fundo da etiqueta com borda
                pdf.set_draw_color(*DARK_CHOC)
                pdf.set_line_width(0.5)
                pdf.rect(x, y, tag_w, tag_h)
                
                # Header "OFERTA" minimalista fundo escuro
                pdf.set_fill_color(*DARK_CHOC)
                pdf.rect(x, y, tag_w, 10, style='F')
                pdf.set_text_color(255, 255, 255)
                pdf.set_font("Arial", 'B', 10)
                pdf.set_xy(x, y)
                pdf.cell(tag_w, 10, txt="  OFERTA EXCLUSIVA", align='L')
                
                # Produto
                pdf.set_text_color(*DARK_CHOC)
                pdf.set_font("Arial", 'B', 14)
                pdf.set_xy(x, y + 15)
                # Multi-cell para evitar estourar limites se for texto longo
                pdf.multi_cell(tag_w, 6, txt=str(produto_nome).upper(), align='C')
                
                # Preços
                pdf.set_xy(x, y + 35)
                if preco_de > 0 and preco_de > preco_por:
                    # Strike/Riscado manual overwrite
                    pdf.set_text_color(120, 120, 120)
                    pdf.set_font("Arial", '', 9) 
                    pdf.cell(tag_w/2, 5, txt=f"De: R$ {preco_de:.2f}", align='R')
                    
                    # Linha cruzada manual over the text
                    pdf.set_draw_color(200, 50, 50)
                    pdf.set_line_width(0.3)
                    pdf.line(x + (tag_w/2) - 18, y + 37, x + (tag_w/2) - 2, y + 37)
                
                # Preço POR Destacado
                pdf.set_xy(x, y + 42)
                pdf.set_text_color(*RED_PROMO)
                pdf.set_font("Arial", 'B', 20)
                pdf.cell(tag_w, 8, txt=f"Por: R$ {preco_por:.2f}", align='C')
                
                count += 1
                
            output = pdf.output(dest='S').encode('latin1')
            st.download_button(label="📥 Baixar Cartelas de Vitrine (Folha A4)", data=output, file_name="Etiquetas_CacauShow.pdf", mime="application/pdf")
            show_feedback(f"Processamento de {qtd_etiquetas} etiquetas concluído!")

    elif cacau_tool == "🛡️ Monitor de Validade":
        st.markdown("### 🛡️ Shelf-Life Proativo")
        st.write("Calculadora inteligente para evitar prejuízos mensurando o vencimento e o tempo de prateleira.")
        from datetime import timedelta
        import datetime
        
        col1, col2 = st.columns(2)
        with col1:
            data_fab = st.date_input("Data de Fabricação do Lote")
        with col2:
            shelf_life_dias = st.number_input("Tempo de Prateleira (Shelf-Life em Dias)", min_value=1, value=120)
            
        if st.button("🔍 Analisar Risco de Vencimento"):
            data_vencimento = data_fab + timedelta(days=shelf_life_dias)
            hoje = datetime.date.today()
            dias_restantes = (data_vencimento - hoje).days
            
            st.divider()
            st.markdown(f"**Data de Vencimento Oficialmente Prevista:** {data_vencimento.strftime('%d/%m/%Y')}")
            
            if dias_restantes < 0:
                st.error(f"🔴 PRODUTO VENCIDO HÁ {abs(dias_restantes)} DIAS! Ação requerida: Descarte imediato e auditoria de perda.")
            elif dias_restantes <= 15:
                st.error(f"🔴 CRÍTICO: Faltam apenas {dias_restantes} dias para o vencimento! Ação requerida: Imediata urgência de escoamento.")
            elif dias_restantes <= 30:
                st.warning(f"🟡 ALERTA: Faltam {dias_restantes} dias para o vencimento. Ação sugerida: Promover queima de estoque.")
            else:
                st.success(f"🟢 SEGURO: Faltam {dias_restantes} dias para o prazo final. O produto transita em estado normal de comercialização.")
            show_feedback("Análise de Shelf-Life Concluída")

    elif cacau_tool == "📅 Gerador de Escala (6x1)":
        st.markdown("### 📅 Gerador de Escala Visual (6x1)")
        st.write("Gera a grade semanal oficial da equipe de loja eliminando processos analógicos complexos.")
        
        # Fora do form para reatividade imediata online
        funcionarios_raw = st.text_area("Lista de Funcionários (Digite estritamente um por linha)", "João Silva\nMaria Souza\nCarlos Mendes\nAna Kelly\nRodrigo E. Teixeira")
        st.info("Otimização Administrativa: Selecione abaixo o dia exato da folga de cada colaborador.")
        
        with st.form("escala_form"):
            dias_semana = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
            lista_funcs = [f.strip() for f in funcionarios_raw.split('\n') if f.strip()]
            
            folgas_selecionadas = {}
            for f in lista_funcs:
                folgas_selecionadas[f] = st.selectbox(f"Dia da Folga para {f}", dias_semana, key=f"folga_{f}")
                
            submit_escala = st.form_submit_button("🗓️ Gerar Quadro de Horários Parametrizado (Escala)")
            
        if submit_escala:
            st.divider()
            st.markdown("#### Grade de Escala 6x1 Consolidada")
            
            # Construir visual corporativo agradável
            html_table = "<table style='width:100%; text-align:center; border-collapse: collapse; margin-top: 15px; margin-bottom: 25px;'>"
            html_table += "<tr style='background-color:#3D1E16; color:#D4AF37; font-weight:bold; font-size: 1.1em;'>"
            html_table += "<th style='padding:12px; border:1px solid #4b2c21; text-align: left;'>Funcionário</th>"
            for d in dias_semana:
                html_table += f"<th style='padding:12px; border:1px solid #4b2c21;'>{d[:3]}</th>"
            html_table += "</tr>"
            
            for f in lista_funcs:
                html_table += "<tr>"
                html_table += f"<td style='padding:12px; border:1px solid #4b2c21; font-weight:bold; text-align:left; color:#ffffff;'>{f}</td>"
                for d in dias_semana:
                    if folgas_selecionadas[f] == d:
                        html_table += f"<td style='padding:12px; border:1px solid #4b2c21; background-color:#da3633; color:white; font-weight:bold;'>FOLGA</td>"
                    else:
                        html_table += f"<td style='padding:12px; border:1px solid #4b2c21; background-color:#2ea043; color:white;'>Trabalha</td>"
                html_table += "</tr>"
            
            html_table += "</table>"
            st.markdown(html_table, unsafe_allow_html=True)
            show_feedback("Escala Semanal Oficial Parametrizada e Pronta.")

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

