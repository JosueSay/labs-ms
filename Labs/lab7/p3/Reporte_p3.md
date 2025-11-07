# Problema 3 - Tests NIST SP 800-22

Para determinar si un generador pseudo-aleatorio cumple estándares de calidad, se recomienda aplicarle una batería de pruebas estadísticas que evalúe uniformidad, independencia y ausencia de patrones deterministas en la secuencia generada.

Por ejemplo, la publicación *A Statistical Test Suite for Random and Pseudorandom Number Generators for Cryptographic Applications* describe una serie de 15 pruebas estadísticas que evalúan distintas propiedades de una secuencia binaria: frecuencia, autocorrelación, bloques, etc.
[https://csrc.nist.gov/projects/random-bit-generation/documentation-and-software?utm_source=chatgpt.com](https://csrc.nist.gov/projects/random-bit-generation/documentation-and-software?utm_source=chatgpt.com)

Investigar cómo implementar en Python la batería de pruebas NIST SP 800-22, y aplicarlas a una lista de 1,000,000 de bits aleatorios generados con el CLG y el Mersenne Twister de los Ejercicios 1 y 2. En Python se puede llamar a las librerías *sts-pylib*, *nistrng*, *sp80022suite* u otras que ya incluyen estos tests.

Elabore una tabla en donde se vea el desempeño de los generadores en cada uno de los tests anteriores, junto con el *p-value* obtenido y concluya cuál de los dos métodos se desempeña mejor.

## Resolución

Se hizo uso de los programas realizados para los incisos 1 y 2 del laboratorio para obtener los datos con los que se trabajaría, que luego se probarian con las preubas NIST, las cuales son estándar internacional. Evalua multiples propiedades, detecta debilidade sutiles y es bastente util en aplicaicones criticas.
