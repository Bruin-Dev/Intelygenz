# Title
Services Architecture

## Date
11/10/2022

## State
PROPOSED

## Context
La actual organización del código en los distintos servicios resulta compleja de entender y de mantener.

Las principales causas y resultados de esta organización y su evolución son:
- falta de estructuras de datos y contratos
- agrupaciones arbitrarias de funcionalidad (utils_repository.py) y nombrados arbitrarios (repository)
- la falta de adherencia a ciertos principios SOLID (principalmente S - Single responsability) y tests unitarios complicados de leer, entender y mantener
- la falta de ACL o adaptadores y acoplamiento con modelos de datos externos
- dispersión de la lógica de negocio

Esta es una serie de tres propuestas que busca poner solución a estos problemas.

__Estas soluciones no buscan tener un caracter retroactivo__

*La propuesta de `Vertical slices` es opcional aunque sería interesante abordarla*

## Object Oriented
### Decision
Todos los datos deben estar modelados en una estructura de datos que corresponda a alguna de estas categorías:
- modelos de dominio
- modelos externos

Los modelos de dominio:
- pueden estar modelados como `@dataclass` de python (el `@dataclass` de python solo proporciona static type checking lo cual en principio debería ser suficiente)
- deben exponer métodos que deriven o transformen sus datos cuando sea necesario
- deben exponer métodos para modificar los datos cuando se deba asegurar cualquier consistencia entre algunos datos

Los modelos externos:
- pueden extender del `BaseModel` de pydantic (proporciona static type checking y runtime type checking lo cual lo hace perfecto para deserializar información externa)
- no deben exponer ningún método

Por sencillez y consistencia es aconsejable que todos los modelos de dominio estén decorados con `@dataclass` de pydantic y que todos los modelos externos extiendan del `BaseModel` de pydantic.

#### Ejemplo de derivación o transformación en modelos de dominio
Evitar:
```
def build_area(square):
  return square["side_length"] * square["side_length"]

def usecase():
  square = {"side_length": 2}
  area = build_area(square=square)
```

Mejor hacer:
```
@dataclass
class Square:
  side_length: int

  def build_area(self):
    return self.side_length * self.side_length

def usecase():
  square = Square(side_length=2)
  area = square.build_area()
```

Dependiendo del caso, también podría ser:
```
@dataclass
class Square:
  side_length: int

  @property
  def area(self):
    return self.side_length * self.side_length

def usecase():
  square = Square(side_length=2)
  area = square.area
```

#### Ejemplo de consistencia en modelos de dominio
Evitar:
```
MAX_GAMEBOY_BATTERIES = 4
gameboy = {"batteries": ["A4", "A4", "A4", "A4"]}

def usecase():
  new_battery = "A4"
  if len(gameboy.batteries) > MAX_GAMEBOY_BATTERIES:
    raise Exception
  else:
    gameboy.batteries.append(new_battery)
```

Mejor hacer:
```
MAX_GAMEBOY_BATTERIES = 4

@dataclass
class Gameboy:
  batteries: List[str]

  def add_battery(battery: str):
    if len(self.batteries) > MAX_GAMEBOY_BATTERIES:
      raise Exception
    else:
      self.batteries.append(new_battery)

gameboy = Gameboy(batteries=["A4", "A4", "A4", "A4"])
    
def usecase():
  new_battery = "A4"
  gameboy.add_battery(new_battery)
```

Mejor aún:
```
@dataclass
class Gameboy:
  max_batteries: int
  batteries: List[str]

  def add_battery(battery: str):
    if len(self.batteries) > self.max_batteries:
      raise Exception
    else:
      self.batteries.append(new_battery)

gameboy = Gameboy(batteries=["A4", "A4", "A4", "A4"], max_batteries=4)
    
def usecase():
  new_battery = "A4"
  gameboy.add_battery(new_battery)
```

### Consequences
#### Positive
- no más tirar del hilo para saber qué datos hay en un dict: basta con consultar la estructura de datos
- contratos más rígidos entre consumidores y proveedores: menos errores inesperados
- ya no hay dispersión de la lógica de negocio: debería quedar centralizada en nuestros modelos de dominio
- desaparece la necesidad de nombres arbitrarios para agrupar funcionalidad como por ejemplo `utils`: las propias estructuras deberían servir de contexto para agrupar funcionalidad
- en un IDE correctamente configurado nos beneficiamos del static type checking

#### Negative
- los servicios que implementen esta decisión no tendrán un código similar al resto de servicios que componen el sistema
- el modelo de dominio requiere de paciencia y mimo

### Alternatives
Ninguna alternativa.

## Clean architecture
### Decision
Todo servicio debe estar construido con las siguientes piezas fundamentales:
- adaptadores de entrada: ACL, desacople entre los datos externos y el caso de uso
- adaptadores de infraestructura: cualquier petición a otro sistema que inicie el servicio (clientes, conexiones con BDD, productores de mensajes, etc...)
- dominio: colección de objetos totalmente desacoplado de cualquier tipo de infraestructura
- casos de uso: capa de aplicación, trabaja con objetos de dominio y con los adaptadores de salida

Aunque no es un caso que se suela dar, puede que sea necesario construir alguna pieza que no pertenezca a ninguna de estas categorías.

#### Adaptadores de entrada
Se lo suele conocer como ACL (Anti-Corruption Layer) y su objetivo es el de desacoplar los contratos externos del contrato del caso de uso.
Deben transformar los datos de entrada a objetos de dominio que entienda el caso de uso.

#### Adaptadores de infraestructura
Su labor es la de interactuar con sistemas externos de los que depende el servicio, ya sea para almacenar datos, consultar datos o producir mensajes.
También funciona como ACL pero a la inversa: debe desacoplar el contrato con el caso de uso de los contratos externos.
Para esto, tanto los argumentos que recibe una pieza de infraestructura como los datos que devuelve deben ser objetos de dominio.
Estas piezas las utiliza exclusivamente el caso de uso así que se deben nombrar utilizando términos ubicuos, nunca utilizando términos técnicos.

Puede darse el caso que se quieran agrupar algunas piezas bajo un contexto común: como métodos de una misma clase, por ejemplo.
Si se llegase a dar, hay que asegurarse que no existe ninguna dependencia entre los métodos.
Es por eso que es aconsejable no precipitarse en agruparlas ya que complica en menor medida la organización de los tests unitarios.

Un ejemplo concreto de este caso sería el concepto de repositorio.
Un repositorio representa una agrupación de operaciones de consulta y escritura de objetos de dominio __cuyo ciclo de vida gestionemos nosotros__
(actualmente no gestionamos el ciclo de vida de ningún objeto dentro del sistema con lo que no deberíamos contar con ningún repositorio).

#### Dominio
El dominio en un servicio es una colección de modelos con comportamiento que centraliza la lógica de dominio del servicio.
Esta colección no debe tener ninguna dependencia con ninguna otra pieza del servicio.

#### Caso de uso
Es la pieza que sabe cómo utilizar los objetos de dominio y las piezas de infraestructura para dar solución a un problema determinado.
Es también la pieza que __mejor se debería leer y entender__ de entre todas las que componen la arquitectura.

### Consequences
#### Positive
- ayudarnos a cumplir con el Single reponsability de los principios SOLID
- desacoplarnos de los modelos de datos externos
- ayudarnos a crear piezas más independientes y de este modo mejorar nuestros tests unitarios

#### Negative
- los servicios que implementen esta decisión no tendrán un código similar al resto de servicios que componen el sistema.

### Alternatives
- N-tier architecture (aunque Clean architecture no deja de ser una implementación de un N-tier architecture con el twist de que la capa de negocio tiene además un dominio desacoplado a modo de sidecar).

## Vertical slices
### Decision
- Las piezas que componen el servicio se deben agrupar por caso de uso en vez de por tipo de componente.
- Se debe asegurar el máximo desacople entre casos de uso, pudiendo contar con el máximo acople entre las piezas que den solución al caso de uso.
- La arquitectura dentro de cada caso de uso debe seguir contando con las piezas fundamentales de Clean architecture en la medida de lo razonable.
- Cada caso de uso se convierte en una suerte de microservicio dentro del microservicio.

Es posible que haya piezas de infraestructura o dominio que __puedan__ compartirse entre casos de uso, pero se debe de tener mucho criterio a la hora de refactorizar.

### Consequences
#### Positive
- es más fácil navegar por el árbol de carpetas y ficheros en el proyecto: todo lo relativo a un caso de uso se encuentra en una misma carpeta
- ayudar a concienciar acerca del impacto que tiene toda pieza compartida entre casos de uso
- ofrece libertad al equipo para implementar la solución al caso de uso sin tener que seguir reglas estrictas (aunque haya que seguir Clean architecture en la medida de lo razonable)
- CQRS out-of-the-box

#### Negative
- los servicios que implementen esta decisión no tendrán un código similar al resto de servicios que componen el sistema.
- puede plantear dudas al principio (aunque una vez que se interioriza es bastante sencillo)
- hay que tener mucho criterio a la hora de refactorizar

### Alternatives
Ninguna
