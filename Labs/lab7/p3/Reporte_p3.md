Tests NIST SP 800-22

Para determinar si un generador pseudo-aleatorio cumple est´andares de calidad, se recomienda aplicarle una bater´ıa de pruebas
estad´ısticas que eval´ue uniformidad, independencia y ausencia de patrones deterministas en la secuencia generada.
Por ejemplio, la publicaci´on A Statistical Test Suite for Random and Pseudorandom Number Generators for Cryptographic
Applications describe una serie de 15 pruebas estad´ısticas que eval´uan distintas propiedades de una secuencia binaria: frecuencia, autocorrelaci´on, bloques, etc.
https://csrc.nist.gov/projects/random-bit-generation/documentation-and-software?utm_source=chatgpt.
com
Investigar c´omo implementar en Python la bater´ıa de pruebas NIST SP 800-22, y aplicarlas a una lista de 1,000,000 de bits
aleatorios generados con el CLG y el Mersenne Twister de los Ejercicios 1 y 2. En Python se puede llamar a las librer´ıas
sts-pylib, nistrng, sp80022suite u otras que ya incluyen estos tests.
Elabore una tabla en donde se vea el desempe˜no de los generadores en cada uno de los test anteriores, junto con el p-value
obtenido y concluya cu´al de los dos m´etodos se desempe˜na mejor.