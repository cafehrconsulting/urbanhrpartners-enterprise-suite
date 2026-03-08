import os
from pathlib import Path
from datetime import datetime

BASE_SGSST_STRUCTURE = {

"00_GOBIERNO_Y_CONTROL":[
"Portada_SGSST.pdf",
"Indice_Maestro.xlsx",
"Control_Documentos.xlsx",
"Control_Registros.xlsx",
"Listado_Maestro_Documental.xlsx",
"Historial_Versiones.xlsx"
],

"01_POLITICA_Y_OBJETIVOS":[
"Politica_SST.pdf",
"Objetivos_SST.pdf",
"Alcance_SGSST.pdf",
"Comunicacion_Politica.pdf"
],

"02_EVALUACION_INICIAL":[
"Evaluacion_Inicial.pdf",
"Autoevaluacion_Estandares_Minimos.xlsx",
"Diagnostico_Brechas.pdf",
"Plan_Mejoramiento_Inicial.xlsx"
],

"03_PLAN_ANUAL":[
"Plan_Anual_Trabajo.xlsx",
"Cronograma_Anual.xlsx",
"Presupuesto_SGSST.xlsx",
"Seguimiento_Plan.xlsx"
],

"04_MATRIZ_LEGAL":[
"Matriz_Legal_SGSST.xlsx",
"Evaluacion_Cumplimiento_Legal.xlsx"
],

"05_ROLES_RESPONSABILIDADES":[
"Asignacion_Responsable_SGSST.pdf",
"Perfil_Responsable.pdf",
"Organigrama_SGSST.pdf",
"Acta_Asignacion_Recursos.pdf"
],

"06_CAPACITACION":[
"Plan_Capacitacion.xlsx",
"Induccion_SST.pdf",
"Reinduccion_SST.pdf"
],

"07_MEDICINA_PREVENTIVA":[
"Profesiogramas.xlsx",
"Examenes_Ocupacionales.xlsx",
"Programas_PyP.xlsx"
],

"08_HIGIENE_SEGURIDAD":[
"Procedimientos_Seguros.pdf",
"Inspecciones_Seguridad.xlsx",
"Condiciones_Locativas.xlsx"
],

"09_MATRIZ_RIESGOS":[
"Matriz_IPVR.xlsx",
"Metodologia_Riesgos.pdf",
"Controles_Implementados.xlsx"
],

"10_EPP":[
"Matriz_EPP_por_Cargo.xlsx",
"Registro_Entrega_EPP.xlsx"
],

"11_EMERGENCIAS":[
"Plan_Emergencias.pdf",
"Analisis_Vulnerabilidad.pdf",
"Simulacros.xlsx"
],

"12_INCIDENTES_ACCIDENTES":[
"Reporte_Incidentes.xlsx",
"Reporte_Accidentes.xlsx",
"Investigaciones.xlsx"
],

"13_AUSENTISMO":[
"Indicadores_Ausentismo.xlsx",
"Base_Eventos_Salud.xlsx"
],

"14_GESTION_CAMBIO":[
"Gestion_Cambio.xlsx"
],

"15_CONTRATISTAS":[
"Requisitos_SST_Contratistas.pdf",
"Evaluacion_Contratistas.xlsx"
],

"16_COPASST":[
"Actas_COPASST.xlsx",
"Eleccion_COPASST.pdf"
],

"17_INDICADORES":[
"Indicadores_SGSST.xlsx",
"Informe_Trimestral.pdf"
],

"18_AUDITORIA":[
"Programa_Auditoria.xlsx",
"Plan_Auditoria.pdf",
"Informe_Auditoria.pdf"
],

"19_PLANES_ACCION":[
"Planes_Accion.xlsx"
],

"20_EVIDENCIAS":[
"Fotos_Inspecciones",
"Fotos_Capacitaciones",
"Fotos_Simulacros"
],

"21_HISTORICO":[
"2024",
"2025",
"Obsoletos"
]

}


class SG_SST_Manager:

    def __init__(self, base_path):

        self.base_path = Path(base_path)

    def create_client_program(self, client_name):

        client_dir = self.base_path / client_name / "SGSST"

        client_dir.mkdir(parents=True, exist_ok=True)

        created_files = []

        for folder, files in BASE_SGSST_STRUCTURE.items():

            folder_path = client_dir / folder
            folder_path.mkdir(exist_ok=True)

            for file in files:

                file_path = folder_path / file

                if "." in file:

                    file_path.touch()

                else:
                    (folder_path / file).mkdir(exist_ok=True)

                created_files.append(str(file_path))

        return created_files