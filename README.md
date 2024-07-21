# Project Title

Este proyecto es parte de una prueba tecnica realizada para N5

### Prerequisites

Qué cosas necesitas instalar el software y cómo instalarlas:
- Tener Docker
- Estar a la altura del proyecto
- Ejecutar: 
    docker-compose build
    docker-compose up
    docker ps
    docker exec -it <contenedor flask> /bin/bash
        flask db init
        flask db migrate "Initial migrate"
        flask db upgrade
- Importar la colección de POSTMAN para probar los servicios

## Estructura del Proyecto Flask
Este proyecto está estructurado siguiendo principios de diseño de software que buscan maximizar la modularidad y mantenibilidad del código. La estructura permite una clara separación de responsabilidades y facilita tanto la escalabilidad como el testing unitario y de integración.

### Motivación de la Estructura
La decisión de dividir el proyecto en distintos módulos y submódulos se basa en los principios de Domain-Driven Design (DDD), que enfatiza la importancia de modelar el software cercano al dominio del negocio. Esto incluye:

* Adaptadores: Se utilizan para permitir la interacción entre diferentes dominios sin necesidad de acceder directamente a los modelos de otros dominios. Esto promueve el desacoplamiento y la reutilización del código, facilitando las pruebas y la mantenibilidad.
Capas claramente definidas: Cada dominio (usuarios, infracciones, vehículos) encapsula su lógica y persistencia, promoviendo la independencia y minimizando las dependencias cruzadas.
* Servicios y Entrypoints: Cada dominio expone su funcionalidad a través de servicios que definen la lógica de negocio, y entrypoints (controladores) que gestionan la interacción con el cliente o con otros sistemas.

### Descripción de la Estructura del Directorio
A continuación se detalla la estructura de directorios del proyecto:

* app/: Contiene toda la lógica del negocio y la configuración de la aplicación.
    * config.py: Configuraciones generales de la aplicación.
    * extensions.py: Extensiones y herramientas comunes como la configuración de la base de datos.
* domain/: Dominios específicos de la aplicación, cada uno con su propia lógica de negocio.
    *infractions/, users/, vehicles/: Cada uno de estos subdirectorios contiene modelos, servicios, entrypoints, y adaptadores específicos del dominio.
* commons/: Funcionalidades comunes como respuestas HTTP personalizadas.
* entrypoint/: Gestiona los entrypoints de nivel superior, proporcionando una interfaz al exterior.
* infrastructure/: Configuraciones de infraestructura como logs.

Esta estructura facilita la navegación y el entendimiento del proyecto, asegurando que el código sea fácil de gestionar y escalar. La utilización de adaptadores para interacciones entre dominios ayuda a mantener el código limpio y desacoplado, ideal para un desarrollo ágil y eficiente.

