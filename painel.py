import os
import string
import secrets
import uuid
import hashlib
import base64
import requests
import qrcode

import questionary
from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich.table import Table
from rich.text import Text

console = Console()

# ================= TÍTULO =================
def mostrar_titulo():
    titulo = Text("M I G U E L", style="bold cyan")
    painel = Panel(
        Align.center(titulo),
        border_style="bright_blue",
        padding=(1, 4),
        title="[bold yellow]PAINEL DE CONTROLE[/bold yellow]",
        subtitle="[dim]Termux Edition[/dim]",
    )
    console.print(painel)

# ================= 01 - IA GERAR CÓDIGO =================
def ia_gerar_codigo():
    prompt = questionary.text("O que você quer que a IA gere?").ask()
    if not prompt:
        return

    api_key = os.getenv("b7d72fa9ac1949d69e9d84ffbb2654a8.OI_fjB2YSzkeujd1jGGyVB0U")
    api_url = os.getenv("IA_API_URL", "https://api.openai.com/v1/chat/completions")
    modelo = os.getenv("IA_MODEL", "gpt-4o-mini")

    if not api_key:
        console.print("[red]⚠️ Configure a variável IA_API_KEY antes.[/red]")
        console.print("[dim]Ex: export IA_API_KEY='sua-chave'[/dim]")
        return

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": modelo,
        "messages": [
            {"role": "system", "content": "Você é um gerador de código. Responda só com o código e comentários curtos."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.3,
    }

    try:
        with console.status("[bold green]🤖 IA pensando..."):
            r = requests.post(api_url, headers=headers, json=payload, timeout=90)
            dados = r.json()
            resposta = dados["choices"][0]["message"]["content"]
            console.print(Panel(resposta, title="🤖 Código Gerado", border_style="green"))
    except Exception as e:
        console.print(f"[red]Erro na IA: {e}[/red]")

# ================= 02 - GERADOR DE SENHA =================
def gerar_senha():
    tamanho = questionary.text("Tamanho da senha:", default="16").ask()
    try:
        tamanho = int(tamanho)
    except ValueError:
        console.print("[red]Digite um número válido.[/red]")
        return
    simbolos = questionary.confirm("Incluir símbolos?").ask()

    chars = string.ascii_letters + string.digits
    if simbolos:
        chars += "!@#$%^&*()-_=+[]{}?"

    senha = "".join(secrets.choice(chars) for _ in range(tamanho))
    console.print(Panel(f"[bold green]{senha}[/bold green]", title="🔐 Senha Gerada"))

# ================= 03 - CONSULTAR IP =================
def consultar_ip():
    console.print("[dim]Consultando seu IP público...[/dim]")
    try:
        r = requests.get(
            "http://ip-api.com/json/?fields=status,country,regionName,city,isp,query,lat,lon,timezone",
            timeout=10,
        )
        d = r.json()
        if d.get("status") != "success":
            console.print("[red]Falha ao consultar IP.[/red]")
            return

        t = Table(title="🌐 Informações do IP")
        t.add_column("Campo", style="cyan")
        t.add_column("Valor", style="white")
        t.add_row("IP", d["query"])
        t.add_row("País", d["country"])
        t.add_row("Estado", d["regionName"])
        t.add_row("Cidade", d["city"])
        t.add_row("Provedor (ISP)", d["isp"])
        t.add_row("Coordenadas", f"{d['lat']}, {d['lon']}")
        t.add_row("Fuso", d["timezone"])
        console.print(t)
    except Exception as e:
        console.print(f"[red]Erro: {e}[/red]")

# ================= 04 - CONSULTAR CEP =================
def consultar_cep():
    cep = questionary.text("Digite o CEP (só números):").ask()
    cep = "".join(filter(str.isdigit, cep or ""))
    if len(cep) != 8:
        console.print("[red]CEP inválido. Precisa ter 8 dígitos.[/red]")
        return

    try:
        r = requests.get(f"https://viacep.com.br/ws/{cep}/json/", timeout=10)
        d = r.json()
        if "erro" in d:
            console.print("[red]CEP não encontrado.[/red]")
            return

        t = Table(title=f"📮 CEP {cep}")
        t.add_column("Campo", style="cyan")
        t.add_column("Valor", style="white")
        for campo in ["logradouro", "complemento", "bairro", "localidade", "uf", "ddd"]:
            t.add_row(campo.capitalize(), d.get(campo) or "-")
        console.print(t)
    except Exception as e:
        console.print(f"[red]Erro: {e}[/red]")

# ================= 05 - GERAR QR CODE =================
def gerar_qrcode():
    texto = questionary.text("Link ou texto para o QR Code:").ask()
    if not texto:
        return
    qr = qrcode.QRCode(border=1)
    qr.add_data(texto)
    qr.make(fit=True)
    console.print(f"\n[bold cyan]QR Code para:[/bold cyan] {texto}\n")
    qr.print_ascii(invert=True)

# ================= 06 - CLIMA =================
def clima():
    cidade = questionary.text("Cidade (ex: Sao Paulo):").ask()
    if not cidade:
        return
    try:
        r = requests.get(f"https://wttr.in/{cidade}?format=3", timeout=10)
        console.print(Panel(r.text.strip(), title="🌤️ Clima"))
    except Exception as e:
        console.print(f"[red]Erro: {e}[/red]")

# ================= 07 - UUID =================
def gerar_uuid():
    novo_uuid = str(uuid.uuid4())
    console.print(Panel(f"[bold green]{novo_uuid}[/bold green]", title="🆔 UUID v4"))

# ================= 08 - ENCURTAR URL =================
def encurtar_url():
    url = questionary.text("Cole a URL longa:").ask()
    if not url:
        return
    try:
        r = requests.get(
            "https://is.gd/create.php",
            params={"format": "simple", "url": url},
            timeout=10,
        )
        if r.status_code == 200 and r.text.startswith("http"):
            console.print(Panel(f"[bold green]{r.text}[/bold green]", title="🔗 URL Encurtada"))
        else:
            console.print(f"[red]Falhou: {r.text}[/red]")
    except Exception as e:
        console.print(f"[red]Erro: {e}[/red]")

# ================= 09 - HASH =================
def gerar_hash():
    texto = questionary.text("Texto para gerar hash:").ask()
    if not texto:
        return
    sha256 = hashlib.sha256(texto.encode()).hexdigest()
    md5 = hashlib.md5(texto.encode()).hexdigest()
    t = Table(title="🔒 Hashes")
    t.add_column("Algoritmo", style="cyan")
    t.add_column("Resultado", style="white")
    t.add_row("MD5", md5)
    t.add_row("SHA-256", sha256)
    console.print(t)

# ================= 10 - BASE64 =================
def base64_tool():
    modo = questionary.select("O que fazer?", choices=["Codificar", "Decodificar"]).ask()
    texto = questionary.text("Texto:").ask()
    if not texto:
        return
    try:
        if modo == "Codificar":
            res = base64.b64encode(texto.encode()).decode()
        else:
            res = base64.b64decode(texto.encode()).decode()
        console.print(Panel(f"[bold green]{res}[/bold green]", title=f"Base64 ({modo})"))
    except Exception as e:
        console.print(f"[red]Erro: {e}[/red]")

# ================= 11 - COTAÇÃO DE MOEDAS =================
def cotacoes():
    try:
        r = requests.get(
            "https://economia.awesomeapi.com.br/json/last/USD-BRL,EUR-BRL,BTC-BRL",
            timeout=10,
        )
        d = r.json()
        t = Table(title="💱 Cotações (em BRL)")
        t.add_column("Moeda", style="cyan")
        t.add_column("Valor", style="green")
        mapa = {"USDBRL": "Dólar (USD)", "EURBRL": "Euro (EUR)", "BTCBRL": "Bitcoin (BTC)"}
        for chave, nome in mapa.items():
            if chave in d:
                t.add_row(nome, f"R$ {float(d[chave]['bid']):,.2f}")
        console.print(t)
    except Exception as e:
        console.print(f"[red]Erro: {e}[/red]")

# ================= MENU =================
def menu():
    escolha = questionary.select(
        "Escolha uma ferramenta:",
        choices=[
            "01 - 🤖 IA: Gerar código",
            "02 - 🔐 Gerador de senha",
            "03 - 🌐 Consultar IP (cidade/local)",
            "04 - 📮 Consultar CEP",
            "05 - 📱 Gerar QR Code",
            "06 - 🌤️  Clima",
            "07 - 🆔 Gerar UUID",
            "08 - 🔗 Encurtar URL",
            "09 - 🔒 Gerar Hash (MD5/SHA256)",
            "10 - 🧬 Base64 (codificar/decodificar)",
            "11 - 💱 Cotação de moedas",
            "00 - 🚪 Sair",
        ],
        style=questionary.Style([
            ("pointer", "fg:#00ffcc bold"),
            ("highlighted", "fg:#00ffcc bold"),
            ("selected", "fg:#00ffcc"),
        ]),
    ).ask()

    acoes = {
        "01": ia_gerar_codigo,
        "02": gerar_senha,
        "03": consultar_ip,
        "04": consultar_cep,
        "05": gerar_qrcode,
        "06": clima,
        "07": gerar_uuid,
        "08": encurtar_url,
        "09": gerar_hash,
        "10": base64_tool,
        "11": cotacoes,
    }

    if escolha.startswith("00"):
        console.print("[dim]Até mais, Miguel! 👋[/dim]")
        return False

    acao = acoes.get(escolha[:2])
    if acao:
        console.print()
        acao()
        console.print()
        questionary.press_any_key_to_continue("Pressione ENTER pra voltar ao menu...").ask()
    return True

# ================= LOOP =================
if __name__ == "__main__":
    mostrar_titulo()
    while True:
        if not menu():
            break