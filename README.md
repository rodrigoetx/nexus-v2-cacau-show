# Nexus OS v2.5 - Command Center ⚡

Um sistema robusto e centralizado construído em Python com Streamlit, projetado como uma **Interface Administrativa de Alta Produtividade** (HUD). Este projeto nasceu da necessidade de unificar diversas ferramentas utilitárias do dia a dia de um administrador, analista ou desenvolvedor em um único ambiente rápido e eficiente.

---

## 🛠️ Ferramentas Integradas (HUD)

O sistema é dividido em "Abas" operacionais modulares, permitindo rápida alternância mental e produtiva:

1. **📄 PDF Forge:** 
   - Mesclagem (Merge) rápida de múltiplos arquivos PDF.
   - Extração de páginas específicas de um PDF enorme.
   - Aplicação de Marca d'Água automatizada.

2. **🖼️ Visual Studio Lite:**
   - Otimização e edição em lote de imagens (Rotação, Resize, Cortes).
   - **Magic Remover**: Remoção mágica de fundos de imagem utilizando IA (`rembg`).

3. **✍️ The Scribe & Summarizer:**
   - **OCR (Optical Character Recognition):** Extração de texto vivo através de fotos ou scans de documentos usando `pytesseract`.
   - Transformador de E-mails: Simulação de PNL para formalização de textos.
   - Summarizer de Reuniões: Geração de Atas e *Action Items* automáticos.

4. **📂 Auto-Organizer:**
   - Varredura cirúrgica de um diretório absoluto no seu disco local, separando dezenas de arquivos caóticos em subpastas organizadas por categoria (PDFs, Imagens, Vídeos, Executáveis) em milissegundos.

5. **🧾 Gerador de Recibo (Padrão CEO):**
   - Motor autônomo baseado no `fpdf` para criar Recibos de Pagamento com qualidade corporativa inquestionável. Preencha o formulário HTML do Streamlit e deixe o backend cuidar das linhas, tabelas e tipografias do PDF.

---

## 🚀 Como Executar o Nexus v2 Localmente

Para operar essa Command Center na sua própria máquina, você precisará ter o Python instalado (3.9+ recomendado).

### 1. Pré-Requisitos (Bibliotecas de Sistema)
O módulo de OCR depende do motor do Tesseract instalado no seu sistema raiz.
- **No Windows:** Baixe o instalador oficial do [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) e adicione o caminho à sua variável de ambiente `PATH`.
- **No Linux/Mac:** Rode `sudo apt install tesseract-ocr` ou `brew install tesseract`.

### 2. Clonando e Instalando Dependências
Clone este repositório e navegue até a pasta instanciada:
```bash
git clone https://github.com/rodrigoetx/nexus-v2-cacau-show.git
cd nexus-v2-cacau-show
```

Crie um ambiente virtual (opcional, porém altamente recomendado) e instale o arquivo de requisitos:
```bash
python -m venv venv
# Ative o venv (Windows: venv\Scripts\activate | Linux: source venv/bin/activate)

pip install -r requirements.txt
```
*(Caso o `requirements.txt` não contemple, instale manualmente os pilares: `pip install streamlit pillow rembg PyPDF2 fpdf pytesseract`)*

### 3. Ligando os Motores
Após garantir suas bibliotecas, tudo o que o NexusOS precisa para engatar o Front-end Web no navegador é o seguinte comando:

```bash
streamlit run app.py
```
*(Opcionalmente, pode rodar o `nexus_format.py` se constar como o script principal do seu commit)*

O terminal subirá um servidor local (`http://localhost:8501`) e seu navegador padrão magicamente abrirá o painel de operações ⚡.

---

### *Reflexão e Evolução*
>*“Utilizo IA e AI Pair Programming não para "terceirizar" a lógica, mas como uma poderosa extensão do raciocínio. O Nexus nasceu como prova desse aumento radical na eficiência de escrita de ferramentas diárias.” — Rodrigo Espinosa.*
