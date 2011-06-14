from geraldo import Report, ReportBand, DetailBand, SystemField, Label, ObjectValue, ReportGroup
from geraldo.utils import cm, BAND_WIDTH, TA_CENTER, TA_RIGHT
from geraldo import Report

class ReporteLineaBase(Report):
	title = 'Lista de items'
	author = 'SAP'

class PruebaReporte(Report):
	class band_detail(DetailBand):
		height = 0.7*cm
		elements = [
			Label(text='Name'),
			ObjectValue(expression='name', left=1.5*cm),
		]
		borders = {'bottom': True}

class LineaBaseReport(Report):
	title = 'Listado de Items'

	class band_detail(DetailBand):
		height = 0.7*cm
		elements = [
			ObjectValue(expression='name', left=0.5*cm),
			ObjectValue(expression='age', left=5*cm),
			#ObjectValue(expression='weight', left=10.5*cm),
		]
		borders = {'bottom': True}

	class band_page_header(ReportBand):
		height = 1.3*cm
		elements = [
			SystemField(expression='%(report_title)s', top=0.1*cm, left=0, width=BAND_WIDTH,
				style={'fontName': 'Helvetica-Bold', 'fontSize': 14, 'alignment': TA_CENTER}),
			SystemField(expression=u'Page %(page_number)d of %(page_count)d', top=0.1*cm,
				width=BAND_WIDTH, style={'alignment': TA_RIGHT}),
			Label(text="Codigo", top=0.8*cm, left=0.5*cm),
			Label(text="Complejidad", top=0.8*cm, left=5*cm),
			#Label(text="Weight", top=0.8*cm, left=10.5*cm),
		]
		borders = {'all': True}
