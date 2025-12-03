#!/usr/bin/env python3
"""
Script para documentar la estructura completa de directorios y archivos.
Genera un reporte detallado con estadísticas y exportación en múltiples formatos.
"""

import os
import json
import datetime
from pathlib import Path
from collections import defaultdict
import argparse


class DocumentadorEstructura:
    def __init__(self, ruta_raiz, ignorar_ocultos=True, ignorar_patrones=None):
        """
        Inicializa el documentador de estructura.
        
        Args:
            ruta_raiz: Directorio raíz a documentar
            ignorar_ocultos: Si True, ignora archivos/directorios ocultos (que empiezan con .)
            ignorar_patrones: Lista de patrones a ignorar (ej: ['__pycache__', 'node_modules'])
        """
        self.ruta_raiz = Path(ruta_raiz).resolve()
        self.ignorar_ocultos = ignorar_ocultos
        self.ignorar_patrones = ignorar_patrones or [
            '__pycache__', 'node_modules', '.git', 'venv', '.env',
            'dist', 'build', '*.pyc', '.DS_Store', 'package-lock.json'
        ]
        
        self.estadisticas = {
            'total_directorios': 0,
            'total_archivos': 0,
            'total_tamaño': 0,
            'extensiones': defaultdict(int),
            'archivos_por_extension': defaultdict(list),
        }
        
        self.estructura = []
        self.directorios_mas_grandes = []
    
    def debe_ignorar(self, ruta):
        """Determina si una ruta debe ser ignorada."""
        nombre = ruta.name
        
        # Ignorar archivos/directorios ocultos
        if self.ignorar_ocultos and nombre.startswith('.'):
            return True
        
        # Ignorar patrones específicos
        for patron in self.ignorar_patrones:
            if patron.startswith('*.'):
                # Patrón de extensión
                if nombre.endswith(patron[1:]):
                    return True
            elif patron in nombre:
                return True
        
        return False
    
    def obtener_tamaño_directorio(self, ruta):
        """Calcula el tamaño total de un directorio."""
        tamaño_total = 0
        try:
            for item in ruta.rglob('*'):
                if item.is_file() and not self.debe_ignorar(item):
                    try:
                        tamaño_total += item.stat().st_size
                    except (PermissionError, FileNotFoundError):
                        pass
        except (PermissionError, FileNotFoundError):
            pass
        return tamaño_total
    
    def formatear_tamaño(self, tamaño_bytes):
        """Convierte bytes a formato legible."""
        for unidad in ['B', 'KB', 'MB', 'GB', 'TB']:
            if tamaño_bytes < 1024.0:
                return f"{tamaño_bytes:.2f} {unidad}"
            tamaño_bytes /= 1024.0
        return f"{tamaño_bytes:.2f} PB"
    
    def escanear_directorio(self, ruta, nivel=0, prefijo=""):
        """Escanea recursivamente un directorio y documenta su estructura."""
        try:
            items = sorted(ruta.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
        except PermissionError:
            self.estructura.append(f"{prefijo}[Permiso Denegado]")
            return
        
        for idx, item in enumerate(items):
            if self.debe_ignorar(item):
                continue
            
            es_ultimo = idx == len(items) - 1
            conector = "└── " if es_ultimo else "├── "
            nuevo_prefijo = prefijo + ("    " if es_ultimo else "│   ")
            
            if item.is_dir():
                self.estadisticas['total_directorios'] += 1
                tamaño_dir = self.obtener_tamaño_directorio(item)
                tamaño_formateado = self.formatear_tamaño(tamaño_dir)
                
                self.estructura.append(f"{prefijo}{conector}📁 {item.name}/ ({tamaño_formateado})")
                self.directorios_mas_grandes.append((item, tamaño_dir))
                
                # Recursión para subdirectorios
                self.escanear_directorio(item, nivel + 1, nuevo_prefijo)
            
            elif item.is_file():
                self.estadisticas['total_archivos'] += 1
                try:
                    tamaño = item.stat().st_size
                    self.estadisticas['total_tamaño'] += tamaño
                    tamaño_formateado = self.formatear_tamaño(tamaño)
                    
                    # Registrar extensión
                    extension = item.suffix.lower() or 'sin_extension'
                    self.estadisticas['extensiones'][extension] += 1
                    self.estadisticas['archivos_por_extension'][extension].append(str(item))
                    
                    # Icono según tipo de archivo
                    icono = self.obtener_icono_archivo(extension)
                    
                    self.estructura.append(
                        f"{prefijo}{conector}{icono} {item.name} ({tamaño_formateado})"
                    )
                except (PermissionError, FileNotFoundError):
                    self.estructura.append(f"{prefijo}{conector}❌ {item.name} [Error de acceso]")
    
    def obtener_icono_archivo(self, extension):
        """Retorna un icono según la extensión del archivo."""
        iconos = {
            '.py': '🐍',
            '.js': '📜',
            '.ts': '📘',
            '.html': '🌐',
            '.css': '🎨',
            '.json': '📋',
            '.md': '📝',
            '.txt': '📄',
            '.pdf': '📕',
            '.jpg': '🖼️',
            '.jpeg': '🖼️',
            '.png': '🖼️',
            '.gif': '🖼️',
            '.svg': '🎭',
            '.mp4': '🎬',
            '.mp3': '🎵',
            '.zip': '📦',
            '.tar': '📦',
            '.gz': '📦',
            '.sql': '🗄️',
            '.db': '🗄️',
            '.yml': '⚙️',
            '.yaml': '⚙️',
            '.xml': '📰',
            '.csv': '📊',
            '.xlsx': '📊',
            '.doc': '📝',
            '.docx': '📝',
        }
        return iconos.get(extension, '📄')
    
    def generar_reporte_texto(self):
        """Genera un reporte en formato texto."""
        lineas = []
        lineas.append("=" * 80)
        lineas.append(f"DOCUMENTACIÓN DE ESTRUCTURA DE DIRECTORIOS")
        lineas.append("=" * 80)
        lineas.append(f"Directorio raíz: {self.ruta_raiz}")
        lineas.append(f"Fecha de generación: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lineas.append("=" * 80)
        lineas.append("")
        
        # Estructura de árbol
        lineas.append("ESTRUCTURA DE ÁRBOL:")
        lineas.append("-" * 80)
        lineas.append(f"📁 {self.ruta_raiz.name}/")
        lineas.extend(self.estructura)
        lineas.append("")
        
        # Estadísticas
        lineas.append("=" * 80)
        lineas.append("ESTADÍSTICAS GENERALES:")
        lineas.append("-" * 80)
        lineas.append(f"Total de directorios: {self.estadisticas['total_directorios']}")
        lineas.append(f"Total de archivos: {self.estadisticas['total_archivos']}")
        lineas.append(f"Tamaño total: {self.formatear_tamaño(self.estadisticas['total_tamaño'])}")
        lineas.append("")
        
        # Extensiones
        lineas.append("DISTRIBUCIÓN POR TIPO DE ARCHIVO:")
        lineas.append("-" * 80)
        extensiones_ordenadas = sorted(
            self.estadisticas['extensiones'].items(),
            key=lambda x: x[1],
            reverse=True
        )
        for ext, count in extensiones_ordenadas:
            lineas.append(f"  {ext}: {count} archivos")
        lineas.append("")
        
        # Directorios más grandes
        lineas.append("DIRECTORIOS MÁS GRANDES (Top 10):")
        lineas.append("-" * 80)
        top_dirs = sorted(self.directorios_mas_grandes, key=lambda x: x[1], reverse=True)[:10]
        for directorio, tamaño in top_dirs:
            lineas.append(f"  {directorio}: {self.formatear_tamaño(tamaño)}")
        lineas.append("")
        
        lineas.append("=" * 80)
        
        return "\n".join(lineas)
    
    def generar_reporte_json(self):
        """Genera un reporte en formato JSON."""
        datos = {
            'directorio_raiz': str(self.ruta_raiz),
            'fecha_generacion': datetime.datetime.now().isoformat(),
            'estadisticas': {
                'total_directorios': self.estadisticas['total_directorios'],
                'total_archivos': self.estadisticas['total_archivos'],
                'total_tamaño_bytes': self.estadisticas['total_tamaño'],
                'total_tamaño_formateado': self.formatear_tamaño(self.estadisticas['total_tamaño']),
                'extensiones': dict(self.estadisticas['extensiones']),
            },
            'estructura': self.estructura,
            'archivos_por_extension': {
                k: v for k, v in self.estadisticas['archivos_por_extension'].items()
            }
        }
        return json.dumps(datos, indent=2, ensure_ascii=False)
    
    def generar_reporte_html(self):
        """Genera un reporte en formato HTML."""
        html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Documentación de Estructura - {self.ruta_raiz.name}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #555;
            margin-top: 30px;
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 5px;
        }}
        .info {{
            background-color: #e3f2fd;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .estructura {{
            background-color: #263238;
            color: #aed581;
            padding: 20px;
            border-radius: 5px;
            overflow-x: auto;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            line-height: 1.6;
            white-space: pre;
        }}
        .estadisticas {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .stat-card {{
            background-color: #f9f9f9;
            padding: 20px;
            border-radius: 5px;
            border-left: 4px solid #4CAF50;
        }}
        .stat-card h3 {{
            margin-top: 0;
            color: #4CAF50;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #4CAF50;
            color: white;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📁 Documentación de Estructura de Directorios</h1>
        
        <div class="info">
            <strong>Directorio raíz:</strong> {self.ruta_raiz}<br>
            <strong>Fecha de generación:</strong> {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
        
        <div class="estadisticas">
            <div class="stat-card">
                <h3>Total Directorios</h3>
                <p style="font-size: 24px; margin: 0;">{self.estadisticas['total_directorios']}</p>
            </div>
            <div class="stat-card">
                <h3>Total Archivos</h3>
                <p style="font-size: 24px; margin: 0;">{self.estadisticas['total_archivos']}</p>
            </div>
            <div class="stat-card">
                <h3>Tamaño Total</h3>
                <p style="font-size: 24px; margin: 0;">{self.formatear_tamaño(self.estadisticas['total_tamaño'])}</p>
            </div>
        </div>
        
        <h2>Estructura de Árbol</h2>
        <div class="estructura">📁 {self.ruta_raiz.name}/
{"".join([line + "\n" for line in self.estructura])}</div>
        
        <h2>Distribución por Tipo de Archivo</h2>
        <table>
            <thead>
                <tr>
                    <th>Extensión</th>
                    <th>Cantidad</th>
                </tr>
            </thead>
            <tbody>
"""
        
        extensiones_ordenadas = sorted(
            self.estadisticas['extensiones'].items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        for ext, count in extensiones_ordenadas:
            html += f"                <tr><td>{ext}</td><td>{count}</td></tr>\n"
        
        html += """
            </tbody>
        </table>
    </div>
</body>
</html>
"""
        return html
    
    def documentar(self):
        """Ejecuta el proceso de documentación completo."""
        print(f"📂 Escaneando directorio: {self.ruta_raiz}")
        print("⏳ Por favor espera...")
        
        self.escanear_directorio(self.ruta_raiz)
        self.directorios_mas_grandes = self.directorios_mas_grandes  # Ya está calculado
        
        print("✅ Escaneo completado!")
        return self


def main():
    parser = argparse.ArgumentParser(
        description='Documenta la estructura completa de directorios y archivos'
    )
    parser.add_argument(
        'ruta',
        nargs='?',
        default='.',
        help='Ruta del directorio a documentar (por defecto: directorio actual)'
    )
    parser.add_argument(
        '-o', '--output',
        default='estructura_documentada',
        help='Nombre base para los archivos de salida (sin extensión)'
    )
    parser.add_argument(
        '-f', '--formato',
        choices=['txt', 'json', 'html', 'todos'],
        default='todos',
        help='Formato de salida (por defecto: todos)'
    )
    parser.add_argument(
        '--incluir-ocultos',
        action='store_true',
        help='Incluir archivos y directorios ocultos'
    )
    parser.add_argument(
        '--ignorar',
        nargs='+',
        help='Patrones adicionales a ignorar'
    )
    
    args = parser.parse_args()
    
    # Crear documentador
    ignorar_patrones = None
    if args.ignorar:
        ignorar_patrones = args.ignorar
    
    doc = DocumentadorEstructura(
        args.ruta,
        ignorar_ocultos=not args.incluir_ocultos,
        ignorar_patrones=ignorar_patrones
    )
    
    # Documentar
    doc.documentar()
    
    # Generar reportes
    formatos_a_generar = ['txt', 'json', 'html'] if args.formato == 'todos' else [args.formato]
    
    for formato in formatos_a_generar:
        nombre_archivo = f"{args.output}.{formato}"
        
        if formato == 'txt':
            contenido = doc.generar_reporte_texto()
        elif formato == 'json':
            contenido = doc.generar_reporte_json()
        elif formato == 'html':
            contenido = doc.generar_reporte_html()
        
        with open(nombre_archivo, 'w', encoding='utf-8') as f:
            f.write(contenido)
        
        print(f"✅ Reporte generado: {nombre_archivo}")
    
    # Mostrar resumen en consola
    print("\n" + "=" * 80)
    print("📊 RESUMEN DE ESTADÍSTICAS")
    print("=" * 80)
    print(f"Total de directorios: {doc.estadisticas['total_directorios']}")
    print(f"Total de archivos: {doc.estadisticas['total_archivos']}")
    print(f"Tamaño total: {doc.formatear_tamaño(doc.estadisticas['total_tamaño'])}")
    print("=" * 80)


if __name__ == '__main__':
    main()