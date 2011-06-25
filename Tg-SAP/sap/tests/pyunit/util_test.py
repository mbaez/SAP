import unittest

from sap.controllers.util import *
from sap import model
import transaction
from tg import config

#imports para graficar los grafos
#import de la libreria de grafo
from sap.lib.pygraph.classes.digraph import *
from sap.lib.pygraph.algorithms.cycles import *

from sap.config.environment import load_environment

class utilTestCase(unittest.TestCase):

	def setUp(self):
		self.util = Util()
		self.proyecto_util = ProyectoUtil()
		self.item_util = ItemUtil()
		self.codigos_generados = []
		#conexion a BD
		db = create_engine('postgresql://postgres:postgres@localhost:5432/sap')
		Session = sessionmaker(bind=db)
		self.session = Session()
		#r = session.query(Proyecto).get(1)
		"""
		usr = model.Usuario()
		usr.id_usr = 5
		usr.user_name = u'test'
		usr.nombre = u'Test'
		usr.email_address = u'test@pyunit.com'
		usr.password = u'test'

		session.add(usr)

		transaction.commit()
		"""

	def runTest(self):
		self.test_gen_codigo()
		self.test_get_user_by_user_name()
		self.test_calculo_impacto()

	def test_gen_codigo(self):
		"""Generacion de codigos unicos"""
		for i in range(10):
			self.codigos_generados.append(self.util.gen_codigo('TEST'))

		assert len(self.codigos_generados) == len(set(self.codigos_generados)),\
			'Existen codigos repetidos'

	def test_get_user_by_user_name(self):
		"""Obtencion de usuario por su codigo"""
		instance = self.session.query(Usuario).filter(Usuario.user_name == 'mbaez').\
												first()
		assert instance.nombre == 'Maxi',\
			'User name no es unico'

	def test_item_aprobados(self):
		"""Solo items aprobados tienen lineas bases"""
		lineas = self.session.query(LineaBase).all()
		error = False
		for linea in lineas:
			if linea.estado.nombre == 'Cerrada':
				items = linea.items
				for item in items:
					#print str(item.id_item)
					if item.estado_actual.nombre != 'Aprobado':
						error = True

		assert not error, 'Existen items no aprobados que tienen lineas base'


if __name__ == "__main__":
	unittest.main()
