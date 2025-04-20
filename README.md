# **Ecommerce-microservices**

# Levantar todos los servicios con Docker Compose
docker-compose up -d

# Verificar que todos los servicios estén corriendo
docker-compose ps

# Registrar un nuevo usuario

POST http://localhost:5000/api/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Juan",
    "lastName": "Pérez",
    "email": "juan@example.com",
    "password": "SecurePass123",
    "phone": "+123456789"
  }'

# Obtener todos los usuarios
GET http://localhost:5000/api/users

# Obtener un usuario específico (reemplazar <user_id> con ID real)
GET http://localhost:5000/api/users/<user_id>

# Actualizar un usuario
PUT http://localhost:5000/api/users/<user_id> \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Juan Carlos",
    "phone": "+987654321"
  }'

# Eliminar un usuario
DELETE http://localhost:5000/api/users/<user_id>

# Login de usuario
POST http://localhost:5000/api/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "juan@example.com",
    "password": "SecurePass123"
  }'

# Verificar health check
GET http://localhost:5000/health

# **Consultas a MongoDB**
# Conectarse a MongoDB
docker exec -it user-service_mongo_1 mongosh ecommerce

# Consultar usuarios registrados
db.users.find().pretty()

# Consultar todos los eventos almacenados
db.events.find().sort({timestamp: -1}).pretty()

# Consultar eventos de registro de usuario
db.events.find({topic: "user-registration"}).pretty()

# Consultar eventos de bienvenida
db.events.find({topic: "welcome-flow"}).pretty()

# Consultar eventos por source
db.events.find({source: "UserService"}).pretty()

# Consultar eventos en un rango de tiempo
db.events.find({
  timestamp: {
    $gte: new Date("2023-10-25T00:00:00Z"),
    $lte: new Date("2023-10-25T23:59:59Z")
  }
}).pretty()

# **Verificar Kafka**
# Listar topics en Kafka
docker exec -it user-service_kafka_1 kafka-topics --list --bootstrap-server localhost:9092

# Consumir mensajes del topic user-registration
docker exec -it user-service_kafka_1 kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic user-registration \
  --from-beginning

# Consumir mensajes del topic welcome-flow
docker exec -it user-service_kafka_1 kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic welcome-flow \
  --from-beginning

# **Ver logs de los servicios**
# Ver logs del user-service
docker logs user-service_user-service_1 -f

# Ver logs de Kafka
docker logs user-service_kafka_1 -f

# Ver logs de MongoDB
docker logs user-service_mongo_1 -f

# **Detener los servicios**
docker-compose down

# Limpiar completamente (elimina volúmenes)
docker-compose down -v
