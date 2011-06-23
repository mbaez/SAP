import unittest

from sap.controllers.util import *
from sap import model
import transaction
from tg import config

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


if __name__ == "__main__":
	unittest.main()
