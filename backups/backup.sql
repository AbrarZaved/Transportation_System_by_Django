-- MySQL dump 10.13  Distrib 8.0.39, for Win64 (x86_64)
--
-- Host: localhost    Database: TRANSPORTATION
-- ------------------------------------------------------
-- Server version	8.0.39

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=57 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',2,'add_permission'),(6,'Can change permission',2,'change_permission'),(7,'Can delete permission',2,'delete_permission'),(8,'Can view permission',2,'view_permission'),(9,'Can add group',3,'add_group'),(10,'Can change group',3,'change_group'),(11,'Can delete group',3,'delete_group'),(12,'Can view group',3,'view_group'),(13,'Can add content type',4,'add_contenttype'),(14,'Can change content type',4,'change_contenttype'),(15,'Can delete content type',4,'delete_contenttype'),(16,'Can view content type',4,'view_contenttype'),(17,'Can add session',5,'add_session'),(18,'Can change session',5,'change_session'),(19,'Can delete session',5,'delete_session'),(20,'Can view session',5,'view_session'),(21,'Can add supervisor',6,'add_supervisor'),(22,'Can change supervisor',6,'change_supervisor'),(23,'Can delete supervisor',6,'delete_supervisor'),(24,'Can view supervisor',6,'view_supervisor'),(25,'Can add bus',7,'add_bus'),(26,'Can change bus',7,'change_bus'),(27,'Can delete bus',7,'delete_bus'),(28,'Can view bus',7,'view_bus'),(29,'Can add driver',8,'add_driver'),(30,'Can change driver',8,'change_driver'),(31,'Can delete driver',8,'delete_driver'),(32,'Can view driver',8,'view_driver'),(33,'Can add route',9,'add_route'),(34,'Can change route',9,'change_route'),(35,'Can delete route',9,'delete_route'),(36,'Can view route',9,'view_route'),(37,'Can add stoppage',10,'add_stoppage'),(38,'Can change stoppage',10,'change_stoppage'),(39,'Can delete stoppage',10,'delete_stoppage'),(40,'Can view stoppage',10,'view_stoppage'),(41,'Can add route stoppage',11,'add_routestoppage'),(42,'Can change route stoppage',11,'change_routestoppage'),(43,'Can delete route stoppage',11,'delete_routestoppage'),(44,'Can view route stoppage',11,'view_routestoppage'),(45,'Can add transportation_schedules',12,'add_transportation_schedules'),(46,'Can change transportation_schedules',12,'change_transportation_schedules'),(47,'Can delete transportation_schedules',12,'delete_transportation_schedules'),(48,'Can view transportation_schedules',12,'view_transportation_schedules'),(49,'Can add student',13,'add_student'),(50,'Can change student',13,'change_student'),(51,'Can delete student',13,'delete_student'),(52,'Can view student',13,'view_student'),(53,'Can add preference',14,'add_preference'),(54,'Can change preference',14,'change_preference'),(55,'Can delete preference',14,'delete_preference'),(56,'Can view preference',14,'view_preference');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `authentication_preference`
--

DROP TABLE IF EXISTS `authentication_preference`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `authentication_preference` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `searched_locations` varchar(100) DEFAULT NULL,
  `student_id` bigint NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `total_searches` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `authentication_prefe_student_id_17326077_fk_authentic` (`student_id`),
  CONSTRAINT `authentication_prefe_student_id_17326077_fk_authentic` FOREIGN KEY (`student_id`) REFERENCES `authentication_student` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `authentication_preference`
--

LOCK TABLES `authentication_preference` WRITE;
/*!40000 ALTER TABLE `authentication_preference` DISABLE KEYS */;
INSERT INTO `authentication_preference` VALUES (8,'Uttara',10,'2025-05-29 18:08:04.687242',15),(9,'Dhanmondi',10,'2025-05-29 18:08:04.687242',27),(11,'Uttara',11,'2025-06-02 06:07:19.971980',21),(12,'Dhanmondi',11,'2025-06-02 10:19:13.678937',14),(13,'Mirpur',10,'2025-06-03 11:33:32.786336',8),(14,'Mirpur',11,'2025-06-17 05:43:06.824006',1);
/*!40000 ALTER TABLE `authentication_preference` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `authentication_student`
--

DROP TABLE IF EXISTS `authentication_student`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `authentication_student` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `student_id` varchar(20) NOT NULL,
  `dept_name` varchar(50) NOT NULL,
  `semester_enrolled` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `student_id` (`student_id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `authentication_student`
--

LOCK TABLES `authentication_student` WRITE;
/*!40000 ALTER TABLE `authentication_student` DISABLE KEYS */;
INSERT INTO `authentication_student` VALUES (10,'Md. Jonayed Hossan','251-15-057','Computer Science & Engineering','Spring 2025'),(11,'MD. ABRAR JAVED SORAFI','221-15-5053','Computer Science & Engineering','Spring 2022');
/*!40000 ALTER TABLE `authentication_student` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `authentication_supervisor`
--

DROP TABLE IF EXISTS `authentication_supervisor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `authentication_supervisor` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `employee_id` varchar(50) NOT NULL,
  `first_name` varchar(255) NOT NULL,
  `last_name` varchar(255) NOT NULL,
  `phone_number` varchar(50) NOT NULL,
  `email` varchar(90) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_admin` tinyint(1) NOT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `last_login` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `employee_id` (`employee_id`),
  UNIQUE KEY `phone_number` (`phone_number`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `authentication_supervisor`
--

LOCK TABLES `authentication_supervisor` WRITE;
/*!40000 ALTER TABLE `authentication_supervisor` DISABLE KEYS */;
INSERT INTO `authentication_supervisor` VALUES (1,'pbkdf2_sha256$870000$PiS8EXdwo9DRRF6ELuQ4Lt$DstMYSWfR4Io2kEzoh7PwExotzbPMTsye3nhGpiByvg=','admin','Abrar','Zaved','01728150570','abrarzaved2002@gmail.com',1,1,1,1,'2025-02-15 07:09:22.653835','2025-06-17 05:38:28.692761');
/*!40000 ALTER TABLE `authentication_supervisor` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_authentic` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_authentic` FOREIGN KEY (`user_id`) REFERENCES `authentication_supervisor` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=105 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
INSERT INTO `django_admin_log` VALUES (1,'2025-02-15 07:11:13.136213','19','Dhanmondi - Sobhanbag',2,'[{\"changed\": {\"fields\": [\"Stoppage name\"]}}]',10,1),(2,'2025-02-15 07:15:26.895791','5','Dhanmondi -> DSC R1',1,'[{\"added\": {}}, {\"added\": {\"name\": \"route stoppage\", \"object\": \"Dhanmondi -> DSC R1 - Stoppage Dhanmondi - Sobhanbag\"}}]',9,1),(3,'2025-02-15 07:20:23.127544','19','Dhanmondi -> DSC R1 - Stoppage Shyamoli Square',1,'[{\"added\": {}}]',11,1),(4,'2025-02-15 07:20:33.313366','5','Dhanmondi -> DSC R1',2,'[{\"added\": {\"name\": \"route stoppage\", \"object\": \"Dhanmondi -> DSC R1 - Stoppage Technical Mor\"}}]',9,1),(5,'2025-02-15 07:21:11.064424','5','Dhanmondi -> DSC R1',2,'[{\"added\": {\"name\": \"route stoppage\", \"object\": \"Dhanmondi -> DSC R1 - Stoppage Majar Road Gabtoli\"}}, {\"added\": {\"name\": \"route stoppage\", \"object\": \"Dhanmondi -> DSC R1 - Stoppage Konabari Bus Stop\"}}, {\"added\": {\"name\": \"route stoppage\", \"object\": \"Dhanmondi -> DSC R1 - Stoppage Eastern Housing\"}}, {\"added\": {\"name\": \"route stoppage\", \"object\": \"Dhanmondi -> DSC R1 - Stoppage Rupnagar\"}}, {\"added\": {\"name\": \"route stoppage\", \"object\": \"Dhanmondi -> DSC R1 - Stoppage Birulia Bus Stand\"}}, {\"added\": {\"name\": \"route stoppage\", \"object\": \"Dhanmondi -> DSC R1 - Stoppage Daffodil Smart City\"}}]',9,1),(6,'2025-02-15 07:22:58.103800','6','DSC -> Dhanmondi R2',1,'[{\"added\": {}}, {\"added\": {\"name\": \"route stoppage\", \"object\": \"DSC -> Dhanmondi R2 - Stoppage Daffodil Smart City\"}}, {\"added\": {\"name\": \"route stoppage\", \"object\": \"DSC -> Dhanmondi R2 - Stoppage Birulia Bus Stand\"}}, {\"added\": {\"name\": \"route stoppage\", \"object\": \"DSC -> Dhanmondi R2 - Stoppage Rupnagar\"}}, {\"added\": {\"name\": \"route stoppage\", \"object\": \"DSC -> Dhanmondi R2 - Stoppage Eastern Housing\"}}, {\"added\": {\"name\": \"route stoppage\", \"object\": \"DSC -> Dhanmondi R2 - Stoppage Konabari Bus Stop\"}}, {\"added\": {\"name\": \"route stoppage\", \"object\": \"DSC -> Dhanmondi R2 - Stoppage Majar Road Gabtoli\"}}, {\"added\": {\"name\": \"route stoppage\", \"object\": \"DSC -> Dhanmondi R2 - Stoppage Technical Mor\"}}, {\"added\": {\"name\": \"route stoppage\", \"object\": \"DSC -> Dhanmondi R2 - Stoppage Shyamoli Square\"}}, {\"added\": {\"name\": \"route stoppage\", \"object\": \"DSC -> Dhanmondi R2 - Stoppage Dhanmondi - Sobhanbag\"}}]',9,1),(7,'2025-02-15 09:21:54.120892','7','Uttara - Rajlokkhi ->Uttara Metro rail Center -> DSC R3',1,'[{\"added\": {}}]',9,1),(8,'2025-02-15 09:23:03.555727','36','Uttara - Rajlokkhi ->Uttara Metro rail Center -> DSC R3 - Stoppage Uttara - Rajlokkhi',1,'[{\"added\": {}}]',11,1),(9,'2025-02-15 09:30:56.011403','7','Uttara - Rajlokkhi ->Uttara Metro rail Center -> DSC R3',2,'[{\"deleted\": {\"name\": \"route stoppage\", \"object\": \"Uttara - Rajlokkhi ->Uttara Metro rail Center -> DSC R3 - Stoppage Beribadh\"}}, {\"deleted\": {\"name\": \"route stoppage\", \"object\": \"Uttara - Rajlokkhi ->Uttara Metro rail Center -> DSC R3 - Stoppage Birulia\"}}, {\"deleted\": {\"name\": \"route stoppage\", \"object\": \"Uttara - Rajlokkhi ->Uttara Metro rail Center -> DSC R3 - Stoppage Daffodil Smart City\"}}, {\"deleted\": {\"name\": \"route stoppage\", \"object\": \"Uttara - Rajlokkhi ->Uttara Metro rail Center -> DSC R3 - Stoppage Diyabari Bridge\"}}, {\"deleted\": {\"name\": \"route stoppage\", \"object\": \"Uttara - Rajlokkhi ->Uttara Metro rail Center -> DSC R3 - Stoppage Grand Zamzam Tower\"}}, {\"deleted\": {\"name\": \"route stoppage\", \"object\": \"Uttara - Rajlokkhi ->Uttara Metro rail Center -> DSC R3 - Stoppage House building\"}}, {\"deleted\": {\"name\": \"route stoppage\", \"object\": \"Uttara - Rajlokkhi ->Uttara Metro rail Center -> DSC R3 - Stoppage Uttara - Rajlokkhi\"}}, {\"deleted\": {\"name\": \"route stoppage\", \"object\": \"Uttara - Rajlokkhi ->Uttara Metro rail Center -> DSC R3 - Stoppage Uttara Metro Rail Center\"}}, {\"deleted\": {\"name\": \"route stoppage\", \"object\": \"Uttara - Rajlokkhi ->Uttara Metro rail Center -> DSC R3 - Stoppage Uttara - Rajlokkhi\"}}]',9,1),(10,'2025-02-15 09:36:56.704553','9','Tongi College gate -> DSC R5',1,'[{\"added\": {}}]',9,1),(11,'2025-02-15 09:38:05.664193','9','Tongi College gate -> DSC R5',2,'[]',9,1),(12,'2025-02-15 09:38:18.457964','10','DSC -> Tongi College gate R6',1,'[{\"added\": {}}]',9,1),(13,'2025-02-15 09:46:50.481041','5','Dhanmondi -> DSC R1',3,'',9,1),(14,'2025-02-15 09:46:50.481989','6','DSC -> Dhanmondi R2',3,'',9,1),(15,'2025-02-15 09:46:50.481989','7','Uttara - Rajlokkhi ->Uttara Metro rail Center -> DSC R3',3,'',9,1),(16,'2025-02-15 09:46:50.481989','8','DSC -> Uttara - Rajlokkhi ->Uttara Metro rail Center R4',3,'',9,1),(17,'2025-02-15 09:46:50.481989','9','Tongi College gate -> DSC R5',3,'',9,1),(18,'2025-02-15 09:46:50.481989','10','DSC -> Tongi College gate R6',3,'',9,1),(19,'2025-02-15 09:46:50.481989','11','ECB Chattor -> Mirpur -> DSC  R7',3,'',9,1),(20,'2025-02-15 09:46:50.481989','12','DSC -> Mirpur -> ECB Chattor R8',3,'',9,1),(21,'2025-02-15 10:41:29.731445','13','Dhanmondi -> DSC R1',2,'[{\"changed\": {\"fields\": [\"From DSC\"]}}]',9,1),(22,'2025-02-15 10:41:38.108545','14','DSC -> Dhanmondi R2',2,'[{\"changed\": {\"fields\": [\"From DSC\"]}}]',9,1),(23,'2025-02-15 10:41:43.816565','13','Dhanmondi -> DSC R1',2,'[{\"changed\": {\"fields\": [\"From DSC\"]}}]',9,1),(24,'2025-02-15 10:41:51.183623','15','Uttara - Rajlokkhi -> Uttara Metro rail Center -> DSC R3',2,'[{\"changed\": {\"fields\": [\"To DSC\"]}}]',9,1),(25,'2025-02-15 10:41:57.469358','16','DSC -> Uttara Metro rail Center -> Uttara - Rajlokkhi R4',2,'[{\"changed\": {\"fields\": [\"Route name\", \"From DSC\"]}}]',9,1),(26,'2025-02-15 10:42:01.924651','17','Tongi College gate -> DSC R5',2,'[{\"changed\": {\"fields\": [\"To DSC\"]}}]',9,1),(27,'2025-02-15 10:42:05.990272','18','DSC -> Tongi College gate R6',2,'[{\"changed\": {\"fields\": [\"From DSC\"]}}]',9,1),(28,'2025-02-15 10:42:11.755389','19','ECB Chattor -> Mirpur -> DSC R7',2,'[{\"changed\": {\"fields\": [\"To DSC\"]}}]',9,1),(29,'2025-02-15 10:42:19.153069','20','DSC -> Mirpur -> ECB Chattor R8',2,'[{\"changed\": {\"fields\": [\"From DSC\"]}}]',9,1),(30,'2025-02-15 10:42:25.733315','21','Konabari Pukur Par -> Zirabo -> Ashulia Bazar -> DSC R9',2,'[{\"changed\": {\"fields\": [\"To DSC\"]}}]',9,1),(31,'2025-02-15 10:42:31.477517','22','DSC -> Ashulia Bazar -> Zirabo -> Konabari Pukur Par R10',2,'[{\"changed\": {\"fields\": [\"From DSC\"]}}]',9,1),(32,'2025-02-15 10:42:37.515651','23','Baipail -> Nabinagar -> C&B -> DSC R11',2,'[{\"changed\": {\"fields\": [\"To DSC\"]}}]',9,1),(33,'2025-02-15 10:42:44.177833','24','DSC -> C&B -> Nabinagar -> Baipail R12',2,'[{\"changed\": {\"fields\": [\"From DSC\"]}}]',9,1),(34,'2025-02-15 10:42:50.139624','25','Dhamrai Bus Stand -> Nabinagar -> C&B -> DSC R13',2,'[{\"changed\": {\"fields\": [\"To DSC\"]}}]',9,1),(35,'2025-02-15 10:43:02.944171','26','DSC -> C&B -> Nabinagar -> Dhamrai Bus Stand R14',2,'[{\"changed\": {\"fields\": [\"From DSC\"]}}]',9,1),(36,'2025-02-15 10:43:10.821485','31','Savar -> C&B -> DSC R15',2,'[{\"changed\": {\"fields\": [\"To DSC\"]}}]',9,1),(37,'2025-02-15 10:43:19.148724','32','DSC -> C&B -> Savar R16',2,'[{\"changed\": {\"fields\": [\"From DSC\"]}}]',9,1),(38,'2025-02-15 12:26:13.047631','1','abrarzaved2002@gmail.com',2,'[{\"changed\": {\"fields\": [\"First name\", \"Last name\", \"Phone number\", \"Email\"]}}]',6,1),(39,'2025-02-15 13:09:53.259371','36','Tongi station route -> DSC R20',2,'[{\"changed\": {\"fields\": [\"Route name\"]}}]',9,1),(40,'2025-02-15 13:19:52.861631','46','Uttara - Rajlokkhi -> Uttara Metro rail Center -> DSC F5',2,'[{\"changed\": {\"fields\": [\"Route name\"]}}]',9,1),(41,'2025-02-15 13:24:18.326364','50','Mirpur-10 -> Sony Cinema Hall -> DSC F9',2,'[{\"changed\": {\"fields\": [\"Route name\"]}}]',9,1),(42,'2025-05-18 16:50:52.547154','1','Surjomukhi 1 erererer',1,'[{\"added\": {}}]',7,1),(43,'2025-05-18 16:51:09.171223','2','Surjomukhi 2 dfdf',1,'[{\"added\": {}}]',7,1),(44,'2025-05-18 16:51:53.453234','1','Abdul Jobbar',1,'[{\"added\": {}}]',8,1),(45,'2025-05-18 16:52:18.570078','2','S. M. Anisuzzaman Ahmed',1,'[{\"added\": {}}]',8,1),(46,'2025-05-18 16:52:39.277841','1','Transportation_schedules object (1)',1,'[{\"added\": {}}]',12,1),(47,'2025-05-18 16:53:03.419198','2','Transportation_schedules object (2)',1,'[{\"added\": {}}]',12,1),(48,'2025-05-20 06:16:20.144429','3','Transportation_schedules object (3)',1,'[{\"added\": {}}]',12,1),(49,'2025-05-20 06:17:11.758586','4','Transportation_schedules object (4)',1,'[{\"added\": {}}]',12,1),(50,'2025-05-20 06:17:21.309185','5','Transportation_schedules object (5)',1,'[{\"added\": {}}]',12,1),(51,'2025-05-27 05:33:06.524028','2','',3,'',13,1),(52,'2025-05-27 06:56:05.780319','4','MD. SHAHRIAR AHMED',3,'',13,1),(53,'2025-05-27 06:56:05.780319','1','MD. ABRAR JAVED SORAFI',3,'',13,1),(54,'2025-05-27 06:56:05.780319','3','MOHAMMAD WALID BIN YOUSUF',3,'',13,1),(55,'2025-05-27 06:56:05.781234','5','Niloy Dey Sarker',3,'',13,1),(56,'2025-05-27 06:56:05.781234','6','REDITA ISLAM KATHA',3,'',13,1),(57,'2025-05-27 15:59:16.236015','8','MD. ABRAR JAVED SORAFI',3,'',13,1),(58,'2025-05-27 15:59:16.236015','7','Md. Jonayed Hossan',3,'',13,1),(59,'2025-05-29 10:33:01.907920','9','Md. Jonayed Hossan',3,'',13,1),(60,'2025-05-29 16:57:54.502126','4','Preference object (4)',3,'',14,1),(61,'2025-05-29 16:57:54.502126','3','Preference object (3)',3,'',14,1),(62,'2025-05-29 16:57:54.503130','2','Preference object (2)',3,'',14,1),(63,'2025-05-29 16:57:54.503130','1','Preference object (1)',3,'',14,1),(64,'2025-05-29 18:13:43.826136','9','Preference object (9)',2,'[{\"changed\": {\"fields\": [\"Total searches\"]}}]',14,1),(65,'2025-05-29 18:13:46.945635','8','Preference object (8)',2,'[{\"changed\": {\"fields\": [\"Total searches\"]}}]',14,1),(66,'2025-06-03 10:36:58.184391','6','Transportation_schedules object (6)',1,'[{\"added\": {}}]',12,1),(67,'2025-06-03 10:38:03.124036','7','Transportation_schedules object (7)',1,'[{\"added\": {}}]',12,1),(68,'2025-06-03 10:38:23.061055','8','Transportation_schedules object (8)',1,'[{\"added\": {}}]',12,1),(69,'2025-06-03 10:38:42.178022','9','Transportation_schedules object (9)',1,'[{\"added\": {}}]',12,1),(70,'2025-06-03 10:38:56.118394','10','Transportation_schedules object (10)',1,'[{\"added\": {}}]',12,1),(71,'2025-06-05 09:01:38.736549','11','Transportation_schedules object (11)',1,'[{\"added\": {}}]',12,1),(72,'2025-06-05 09:09:49.394062','11','Transportation_schedules object (11)',2,'[]',12,1),(73,'2025-06-05 09:12:02.776450','1','Transportation_schedules object (1)',2,'[{\"changed\": {\"fields\": [\"From dsc\", \"To dsc\"]}}]',12,1),(74,'2025-06-05 16:40:07.741841','10','Transportation_schedules object (10)',2,'[{\"changed\": {\"fields\": [\"Departure time\"]}}]',12,1),(75,'2025-06-05 16:40:29.576516','10','Transportation_schedules object (10)',2,'[{\"changed\": {\"fields\": [\"Departure time\"]}}]',12,1),(76,'2025-06-05 16:41:32.748915','11','Transportation_schedules object (11)',2,'[{\"changed\": {\"fields\": [\"Departure time\"]}}]',12,1),(77,'2025-06-06 16:27:36.003143','11','Transportation_schedules object (11)',2,'[{\"changed\": {\"fields\": [\"Days\"]}}]',12,1),(78,'2025-06-06 16:27:51.674396','10','Transportation_schedules object (10)',2,'[{\"changed\": {\"fields\": [\"Days\"]}}]',12,1),(79,'2025-06-06 16:28:02.594014','2','Transportation_schedules object (2)',2,'[{\"changed\": {\"fields\": [\"Days\"]}}]',12,1),(80,'2025-06-06 16:28:10.247339','4','Transportation_schedules object (4)',2,'[{\"changed\": {\"fields\": [\"Days\"]}}]',12,1),(81,'2025-06-06 16:28:17.457419','6','Transportation_schedules object (6)',2,'[{\"changed\": {\"fields\": [\"Days\"]}}]',12,1),(82,'2025-06-06 16:28:24.832132','7','Transportation_schedules object (7)',2,'[{\"changed\": {\"fields\": [\"Days\"]}}]',12,1),(83,'2025-06-06 16:28:35.511109','8','Transportation_schedules object (8)',2,'[{\"changed\": {\"fields\": [\"Days\"]}}]',12,1),(84,'2025-06-06 16:28:48.511944','1','Transportation_schedules object (1)',2,'[{\"changed\": {\"fields\": [\"Days\"]}}]',12,1),(85,'2025-06-06 16:43:25.250706','11','Transportation_schedules object (11)',2,'[{\"changed\": {\"fields\": [\"Days\"]}}]',12,1),(86,'2025-06-06 16:44:03.446441','11','Transportation_schedules object (11)',2,'[{\"changed\": {\"fields\": [\"Departure time\"]}}]',12,1),(87,'2025-06-06 16:44:25.832900','11','Transportation_schedules object (11)',2,'[{\"changed\": {\"fields\": [\"Departure time\"]}}]',12,1),(88,'2025-06-06 16:45:21.409227','11','Transportation_schedules object (11)',2,'[{\"changed\": {\"fields\": [\"Departure time\"]}}]',12,1),(89,'2025-06-06 16:45:33.654831','11','Transportation_schedules object (11)',2,'[{\"changed\": {\"fields\": [\"Departure time\"]}}]',12,1),(90,'2025-06-06 16:47:02.468866','11','Transportation_schedules object (11)',2,'[{\"changed\": {\"fields\": [\"Departure time\"]}}]',12,1),(91,'2025-06-06 16:50:06.215640','10','Transportation_schedules object (10)',2,'[{\"changed\": {\"fields\": [\"Days\"]}}]',12,1),(92,'2025-06-06 16:50:31.885848','10','Transportation_schedules object (10)',2,'[]',12,1),(93,'2025-06-06 16:51:04.388822','10','Transportation_schedules object (10)',3,'',12,1),(94,'2025-06-06 16:52:30.588033','7','Transportation_schedules object (7)',2,'[{\"changed\": {\"fields\": [\"Departure time\"]}}]',12,1),(95,'2025-06-06 16:53:35.317740','6','Transportation_schedules object (6)',2,'[{\"changed\": {\"fields\": [\"Departure time\"]}}]',12,1),(96,'2025-06-06 17:14:15.611212','11','Transportation_schedules object (11)',2,'[{\"changed\": {\"fields\": [\"Departure time\"]}}]',12,1),(97,'2025-06-06 17:25:37.195379','11','Transportation_schedules object (11)',2,'[{\"changed\": {\"fields\": [\"Departure time\"]}}]',12,1),(98,'2025-06-06 17:26:07.559738','7','Transportation_schedules object (7)',2,'[{\"changed\": {\"fields\": [\"Departure time\"]}}]',12,1),(99,'2025-06-06 17:27:16.581962','7','Transportation_schedules object (7)',2,'[{\"changed\": {\"fields\": [\"Departure time\"]}}]',12,1),(100,'2025-06-08 06:02:14.209392','2','Transportation_schedules object (2)',2,'[{\"changed\": {\"fields\": [\"Days\"]}}]',12,1),(101,'2025-06-08 06:02:50.265886','2','Transportation_schedules object (2)',2,'[{\"changed\": {\"fields\": [\"Days\"]}}]',12,1),(102,'2025-06-17 05:39:08.159890','5','Transportation_schedules object (5)',2,'[{\"changed\": {\"fields\": [\"Days\", \"Departure time\"]}}]',12,1),(103,'2025-06-17 05:39:55.780570','4','Transportation_schedules object (4)',2,'[{\"changed\": {\"fields\": [\"Departure time\"]}}]',12,1),(104,'2025-06-17 05:40:19.516507','3','Transportation_schedules object (3)',2,'[{\"changed\": {\"fields\": [\"Route\", \"Days\", \"Departure time\", \"From dsc\", \"To dsc\"]}}]',12,1);
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (1,'admin','logentry'),(3,'auth','group'),(2,'auth','permission'),(14,'authentication','preference'),(13,'authentication','student'),(6,'authentication','supervisor'),(4,'contenttypes','contenttype'),(5,'sessions','session'),(7,'transit_hub','bus'),(8,'transit_hub','driver'),(9,'transit_hub','route'),(11,'transit_hub','routestoppage'),(10,'transit_hub','stoppage'),(12,'transport_manager','transportation_schedules');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2025-02-15 07:09:11.212137'),(2,'authentication','0001_initial','2025-02-15 07:09:11.233804'),(3,'admin','0001_initial','2025-02-15 07:09:11.398620'),(4,'admin','0002_logentry_remove_auto_add','2025-02-15 07:09:11.414270'),(5,'admin','0003_logentry_add_action_flag_choices','2025-02-15 07:09:11.414270'),(6,'contenttypes','0002_remove_content_type_name','2025-02-15 07:09:11.483962'),(7,'auth','0001_initial','2025-02-15 07:09:11.780415'),(8,'auth','0002_alter_permission_name_max_length','2025-02-15 07:09:11.852213'),(9,'auth','0003_alter_user_email_max_length','2025-02-15 07:09:11.867837'),(10,'auth','0004_alter_user_username_opts','2025-02-15 07:09:11.867837'),(11,'auth','0005_alter_user_last_login_null','2025-02-15 07:09:11.867837'),(12,'auth','0006_require_contenttypes_0002','2025-02-15 07:09:11.883460'),(13,'auth','0007_alter_validators_add_error_messages','2025-02-15 07:09:11.883460'),(14,'auth','0008_alter_user_username_max_length','2025-02-15 07:09:11.883460'),(15,'auth','0009_alter_user_last_name_max_length','2025-02-15 07:09:11.902005'),(16,'auth','0010_alter_group_name_max_length','2025-02-15 07:09:11.928024'),(17,'auth','0011_update_proxy_permissions','2025-02-15 07:09:11.937988'),(18,'auth','0012_alter_user_first_name_max_length','2025-02-15 07:09:11.939053'),(19,'sessions','0001_initial','2025-02-15 07:09:11.982394'),(20,'transit_hub','0001_initial','2025-02-15 07:09:12.080052'),(21,'transit_hub','0002_stoppage_remove_route_route_distance_and_more','2025-02-15 07:09:12.741428'),(22,'transport_manager','0001_initial','2025-02-15 07:09:13.134533'),(23,'transport_manager','0002_remove_transportation_schedules_arrival_time','2025-02-15 07:09:13.166416'),(24,'transport_manager','0003_transportation_schedules_audience_and_more','2025-02-15 07:09:13.317599'),(25,'transit_hub','0003_alter_routestoppage_created_at','2025-02-15 07:13:08.123237'),(26,'transit_hub','0004_alter_routestoppage_unique_together','2025-02-15 07:16:54.852760'),(27,'transit_hub','0005_alter_routestoppage_created_at','2025-02-15 07:18:54.617998'),(28,'transit_hub','0006_alter_routestoppage_unique_together','2025-02-15 07:20:21.072580'),(29,'transit_hub','0007_alter_routestoppage_options','2025-02-15 09:16:43.189858'),(30,'transit_hub','0008_alter_route_from_dsc_alter_route_to_dsc','2025-02-15 09:19:23.292539'),(31,'authentication','0002_student','2025-05-27 05:01:12.168361'),(32,'authentication','0003_rename_first_name_student_name_and_more','2025-05-27 05:21:03.269589'),(33,'authentication','0004_preference','2025-05-29 10:10:32.775822'),(34,'authentication','0005_preference_created_at_preference_total_searches','2025-05-29 18:08:04.891122'),(35,'transport_manager','0004_transportation_schedules_days','2025-06-06 16:24:04.890959'),(36,'transport_manager','0005_alter_transportation_schedules_days','2025-06-06 16:26:15.412428'),(37,'transport_manager','0006_alter_transportation_schedules_departure_time','2025-06-06 16:30:51.263730');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES ('3gxzklzta1htuk5nk1y8ztanu3hbtvdp','eyJzdHVkZW50X2lkIjoiMjUxLTE1LTA1NyIsImlzX3N0dWRlbnRfYXV0aGVudGljYXRlZCI6dHJ1ZSwiX3Nlc3Npb25fZXhwaXJ5IjozNjAwfQ:1uKhap:2WldXZmQfhk4uFw5UaiAFLFYUfBEiMDL3pPRiOLb-yk','2025-05-29 19:03:03.607274'),('5vq9nd5g559by9ig5fyjox9q8r4waiy7','eyJzdHVkZW50X2lkIjoiMjUxLTE1LTA1NyIsImlzX3N0dWRlbnRfYXV0aGVudGljYXRlZCI6dHJ1ZSwiX3Nlc3Npb25fZXhwaXJ5IjozNjAwfQ:1uKgZN:KkXEzOX__BK_uvnBL2eyMMOC_qOyy2OIOaWiQyVT3Zw','2025-05-29 17:57:29.321155'),('5yza1vu723dj6a6bpct0cbk9tvvr1qen','eyJzdHVkZW50X2lkIjoiMjUxLTE1LTA1NyIsImlzX3N0dWRlbnRfYXV0aGVudGljYXRlZCI6dHJ1ZSwiX3Nlc3Npb25fZXhwaXJ5IjozNjAwfQ:1uKtY7:bvUGfjGJ4qNcDiojal0k7pobCcDiuG6YOKlBMunBOmw','2025-05-30 07:49:03.940701'),('9tquqm0fd59mh3ywu3hggpynxeaono29','eyJzdHVkZW50X2lkIjoiMjUxLTE1LTA1NyIsImlzX3N0dWRlbnRfYXV0aGVudGljYXRlZCI6dHJ1ZSwiX3Nlc3Npb25fZXhwaXJ5IjozNjAwfQ:1uMPrq:3wp-VwhhzIcQuoEbDnXLKe3ltKcpT7GTgvxPrNudLec','2025-06-03 12:31:42.418144'),('anktzgy81v68ra1okkozvl8r8dp1bvk0','eyJzdHVkZW50X2lkIjoiMjIxLTE1LTUzMjgiLCJpc19zdHVkZW50X2F1dGhlbnRpY2F0ZWQiOnRydWUsIl9zZXNzaW9uX2V4cGlyeSI6MzYwMH0:1uJoCb:zY4-mtCd51-7DrcWl6LkR4_CJAyBmHKDRJbb16r4Ll8','2025-05-27 07:54:21.593658'),('d017jptg5rancl7327rnfgso6l22ybzh','eyJzdHVkZW50X2lkIjoiMjIxLTE1LTUwNTMiLCJpc19zdHVkZW50X2F1dGhlbnRpY2F0ZWQiOnRydWUsIl9zZXNzaW9uX2V4cGlyeSI6MzYwMH0:1uL0i7:-y25wkThUDkYhhETFJcsMo5_XHHuSKRl6xtcMuG4Lws','2025-05-30 15:27:51.734474'),('dv3muocp2jp3zizgvo3tp3yrel2pwcoa','eyJzdHVkZW50X2lkIjoiMjIxLTE1LTUwNTMiLCJpc19zdHVkZW50X2F1dGhlbnRpY2F0ZWQiOnRydWUsIl9zZXNzaW9uX2V4cGlyeSI6MzYwMH0:1uLR1W:mht6ptHJr3KSKfg1Too2HKyuQ6uSShyXoObQwexqmIg','2025-05-31 19:33:38.852802'),('fl5h2gll6gqgfgl4q1eia2gq98ct82ca','.eJxVjMsOwiAQRf-FtSHgDI-6dO83kAGmUjWQlHZl_HfbpAvdnnPufYtA61LC2nkOUxYXocXpl0VKT667yA-q9yZTq8s8Rbkn8rBd3lrm1_Vo_w4K9bKtCSCzIkxnspC9opFROefYREjRg9WGCckNA2sYlUGLZkOaAb13PorPF-g_N3E:1uRP1g:f0sv0cw8lXRXFrpmmMUXwL77R833wL33_OKwu0gu_HM','2025-07-01 05:38:28.698759'),('h8if6e8pwvnoaf1dzg87lm02o3fbx17s','eyJzdHVkZW50X2lkIjoiMjIxLTE1LTUwNTMiLCJpc19zdHVkZW50X2F1dGhlbnRpY2F0ZWQiOnRydWUsIl9zZXNzaW9uX2V4cGlyeSI6MzYwMH0:1uMPL1:oMmmBm64YWgX-I5YJoTHd83Of2z9IkJJYql6vBVv5Ns','2025-06-03 11:57:47.128180'),('jkate3dokjofrgomo8qitffno40tymwv','eyJzdHVkZW50X2lkIjoiMjIxLTE1LTUwNTMiLCJpc19zdHVkZW50X2F1dGhlbnRpY2F0ZWQiOnRydWUsIl9zZXNzaW9uX2V4cGlyeSI6MzYwMH0:1uLyMX:yXBvYQt-NiU5jeRQKsExDcNnZEc9TPMur4uMdVU-7Bk','2025-06-02 07:09:33.297703'),('lb5xv1rc4wxu75ro2j8yv9of6d5qzctg','eyJzdHVkZW50X2lkIjoiMjUxLTE1LTA1NyIsImlzX3N0dWRlbnRfYXV0aGVudGljYXRlZCI6dHJ1ZSwiX3Nlc3Npb25fZXhwaXJ5IjozNjAwfQ:1uMOv4:ov-D0cH5yLreiV6eylaxo7EpdAdnYEDa-K1Z4liatqU','2025-06-03 11:30:58.487144'),('ouourlmginnb6bcp7qeifafq2lmdoxet','.eJxVjMsOwiAQRf-FtSHgDI-6dO83kAGmUjWQlHZl_HfbpAvdnnPufYtA61LC2nkOUxYXocXpl0VKT667yA-q9yZTq8s8Rbkn8rBd3lrm1_Vo_w4K9bKtCSCzIkxnspC9opFROefYREjRg9WGCckNA2sYlUGLZkOaAb13PorPF-g_N3E:1uMPKL:I5iMHe4RO1Tjd5Z4oDemkydo0Ljb6tjARm6He-d87oI','2025-06-17 10:57:05.485136'),('qgtuw2jglqwehdd0z6e8l1s3xvvxtxg0','eyJzdHVkZW50X2lkIjoiMjUxLTE1LTA1NyIsImlzX3N0dWRlbnRfYXV0aGVudGljYXRlZCI6dHJ1ZSwiX3Nlc3Npb25fZXhwaXJ5IjozNjAwfQ:1uKbNk:BoQ4Ln-jC4DAP4Te_wMlp9rsybsuFg-g3mRr76NIxVg','2025-05-29 12:25:08.455521'),('qqaga7fwekco2d0qo4hcr3xnjbgwgx3u','eyJzdHVkZW50X2lkIjoiMjUxLTE1LTA1NyIsImlzX3N0dWRlbnRfYXV0aGVudGljYXRlZCI6dHJ1ZSwiX3Nlc3Npb25fZXhwaXJ5IjozNjAwfQ:1uKsdr:e2djhrhmD-hHZPoLx638kqK5sDiPnsCw1ApqmMruSyw','2025-05-30 06:50:55.673640'),('vt5w4is5bwho0kfz1zo814xqs29a07q7','.eJxVjMsOwiAQRf-FtSHgDI-6dO83kAGmUjWQlHZl_HfbpAvdnnPufYtA61LC2nkOUxYXocXpl0VKT667yA-q9yZTq8s8Rbkn8rBd3lrm1_Vo_w4K9bKtCSCzIkxnspC9opFROefYREjRg9WGCckNA2sYlUGLZkOaAb13PorPF-g_N3E:1tjCIt:L8qxWcimpTnuOYVULtW7LUo3BuxMJrPI_KgwiV27YT4','2025-03-01 07:09:31.151659'),('w60nm9gullr209t0tj275f6htfdzbf36','eyJzdHVkZW50X2lkIjoiMjUxLTE1LTA1NyIsImlzX3N0dWRlbnRfYXV0aGVudGljYXRlZCI6dHJ1ZSwiX3Nlc3Npb25fZXhwaXJ5IjozNjAwfQ:1uRPD2:MPKdUyMiiwZOzNmR11Wn3unJ2OXDhDjvnBVexetQc_o','2025-06-17 06:50:12.450213'),('whqv6glt1xohd8g1hdtpeq7qc5izso7y','.eJxVjMsOwiAQRf-FtSHgDI-6dO83kAGmUjWQlHZl_HfbpAvdnnPufYtA61LC2nkOUxYXocXpl0VKT667yA-q9yZTq8s8Rbkn8rBd3lrm1_Vo_w4K9bKtCSCzIkxnspC9opFROefYREjRg9WGCckNA2sYlUGLZkOaAb13PorPF-g_N3E:1tp07d:nYcUwgR9-lFFuTTHlNs94mMQCJLjBbhEyAkPEUp8WaY','2025-03-17 07:21:53.644991'),('yzqfvjrhsvqwwfhv6vwjyozvfrpfatfz','eyJzdHVkZW50X2lkIjoiMjUxLTE1LTA1NyIsImlzX3N0dWRlbnRfYXV0aGVudGljYXRlZCI6dHJ1ZSwiX3Nlc3Npb25fZXhwaXJ5IjozNjAwfQ:1uKhX9:gKYar_LUryhMRFaSv5e8pxKRiu92tgBIrOtU_xu4DaU','2025-05-29 18:59:15.727504');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `transit_hub_bus`
--

DROP TABLE IF EXISTS `transit_hub_bus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `transit_hub_bus` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `bus_name` varchar(100) NOT NULL,
  `bus_number` varchar(30) NOT NULL,
  `bus_model` varchar(30) NOT NULL,
  `bus_capacity` int NOT NULL,
  `bus_photo` varchar(100) NOT NULL,
  `bus_status` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `transit_hub_bus_bus_name_bus_number_39582fb6_uniq` (`bus_name`,`bus_number`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `transit_hub_bus`
--

LOCK TABLES `transit_hub_bus` WRITE;
/*!40000 ALTER TABLE `transit_hub_bus` DISABLE KEYS */;
INSERT INTO `transit_hub_bus` VALUES (1,'Surjomukhi 1','erererer','ererdfdf',30,'bus_photos/Screenshot_2025-05-01_132244.png',1,'2025-05-18 16:50:52.526900','2025-05-18 16:50:52.526900'),(2,'Surjomukhi 2','dfdf','vctgret',30,'bus_photos/wp2933291-iron-man-wallpaper-for-android-hd.jpg',1,'2025-05-18 16:51:09.167096','2025-05-18 16:51:09.167096');
/*!40000 ALTER TABLE `transit_hub_bus` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `transit_hub_driver`
--

DROP TABLE IF EXISTS `transit_hub_driver`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `transit_hub_driver` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `first_name` varchar(30) NOT NULL,
  `last_name` varchar(30) NOT NULL,
  `phone_number` varchar(15) NOT NULL,
  `license_number` varchar(30) NOT NULL,
  `license_expiry` date NOT NULL,
  `license_class` varchar(10) NOT NULL,
  `license_country` varchar(30) NOT NULL,
  `license_issued` date NOT NULL,
  `license_photo` varchar(100) DEFAULT NULL,
  `driver_photo` varchar(100) DEFAULT NULL,
  `driver_status` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `transit_hub_driver_phone_number_license_number_fddd51f9_uniq` (`phone_number`,`license_number`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `transit_hub_driver`
--

LOCK TABLES `transit_hub_driver` WRITE;
/*!40000 ALTER TABLE `transit_hub_driver` DISABLE KEYS */;
INSERT INTO `transit_hub_driver` VALUES (1,'Abdul','Jobbar','01728150570','4346456','2025-05-18','A','Bangladesh','2025-05-18','license_photos/476185318_2031482427279993_5316212448159537604_n.jpg','driver_photos/IMG_2223.jpg',1,'2025-05-18 16:51:53.437195','2025-05-18 16:51:53.437195'),(2,'S. M. Anisuzzaman','Ahmed','017281505700','4346456ere','2025-05-18','C','Bangladesh','2025-05-18','license_photos/Screenshot_2025-02-25_183443.png','driver_photos/Screenshot_2025-02-25_211126.png',1,'2025-05-18 16:52:18.564141','2025-05-18 16:52:18.564141');
/*!40000 ALTER TABLE `transit_hub_driver` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `transit_hub_route`
--

DROP TABLE IF EXISTS `transit_hub_route`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `transit_hub_route` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `route_name` varchar(100) NOT NULL,
  `route_number` varchar(30) NOT NULL,
  `route_status` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `from_dsc` tinyint(1) NOT NULL,
  `to_dsc` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `transit_hub_route_route_name_route_number_c4ee4237_uniq` (`route_name`,`route_number`)
) ENGINE=InnoDB AUTO_INCREMENT=52 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `transit_hub_route`
--

LOCK TABLES `transit_hub_route` WRITE;
/*!40000 ALTER TABLE `transit_hub_route` DISABLE KEYS */;
INSERT INTO `transit_hub_route` VALUES (13,'Dhanmondi -> DSC','R1',1,'2025-02-15 09:48:41.509222','2025-02-15 10:41:43.815541',0,1),(14,'DSC -> Dhanmondi','R2',1,'2025-02-15 09:49:20.640115','2025-02-15 10:41:38.101996',1,0),(15,'Uttara - Rajlokkhi -> Uttara Metro rail Center -> DSC','R3',1,'2025-02-15 09:50:17.473218','2025-02-15 10:41:51.180609',0,1),(16,'DSC -> Uttara Metro rail Center -> Uttara - Rajlokkhi','R4',1,'2025-02-15 09:50:58.470970','2025-02-15 10:41:57.458922',1,0),(17,'Tongi College gate -> DSC','R5',1,'2025-02-15 09:52:18.526753','2025-02-15 10:42:01.920632',0,1),(18,'DSC -> Tongi College gate','R6',1,'2025-02-15 09:52:49.879774','2025-02-15 10:42:05.987273',1,0),(19,'ECB Chattor -> Mirpur -> DSC','R7',1,'2025-02-15 09:53:35.072496','2025-02-15 10:42:11.752467',0,1),(20,'DSC -> Mirpur -> ECB Chattor','R8',1,'2025-02-15 09:54:32.831383','2025-02-15 10:42:19.151091',1,0),(21,'Konabari Pukur Par -> Zirabo -> Ashulia Bazar -> DSC','R9',1,'2025-02-15 09:55:55.848777','2025-02-15 10:42:25.721142',0,1),(22,'DSC -> Ashulia Bazar -> Zirabo -> Konabari Pukur Par','R10',1,'2025-02-15 09:56:46.862413','2025-02-15 10:42:31.471070',1,0),(23,'Baipail -> Nabinagar -> C&B -> DSC','R11',1,'2025-02-15 09:57:30.866960','2025-02-15 10:42:37.509847',0,1),(24,'DSC -> C&B -> Nabinagar -> Baipail','R12',1,'2025-02-15 09:58:25.618447','2025-02-15 10:42:44.177833',1,0),(25,'Dhamrai Bus Stand -> Nabinagar -> C&B -> DSC','R13',1,'2025-02-15 09:59:24.514570','2025-02-15 10:42:50.137584',0,1),(26,'DSC -> C&B -> Nabinagar -> Dhamrai Bus Stand','R14',1,'2025-02-15 10:01:54.477126','2025-02-15 10:43:02.939273',1,0),(31,'Savar -> C&B -> DSC','R15',1,'2025-02-15 10:28:47.539650','2025-02-15 10:43:10.819811',0,1),(32,'DSC -> C&B -> Savar','R16',1,'2025-02-15 10:29:26.856684','2025-02-15 10:43:19.142732',1,0),(33,'Narayanganj Chasara ->  Dhanmondi -> DSC','R17',1,'2025-02-15 10:38:37.638368','2025-02-15 10:38:37.638368',0,1),(34,'Green Model Town -> Mugdha Model Thana -> Malibag -> Rampura -> DSC','R18',1,'2025-02-15 10:40:19.306001','2025-02-15 10:40:19.306001',0,1),(35,'DSC -> Rampura -> Malibag -> Mugdha Model Thana -> Green Model Town','R19',1,'2025-02-15 10:40:58.861540','2025-02-15 10:40:58.861540',1,0),(36,'Tongi station route -> DSC','R20',1,'2025-02-15 13:08:31.742053','2025-02-15 13:09:53.253986',0,1),(37,'DSC -> Tongi station route','R21',1,'2025-02-15 13:10:33.927341','2025-02-15 13:10:33.927341',1,0),(38,'Mirpur-1 -> Sony Cinema Hall -> DSC','R22',1,'2025-02-15 13:11:34.879528','2025-02-15 13:11:34.879528',0,1),(39,'DSC -> Sony Cinema Hall -> Mirpur-1','R23',1,'2025-02-15 13:12:58.017746','2025-02-15 13:12:58.017746',1,0),(40,'Uttara Moylar Mor -> Uttara Metro rail Center -> DSC','R24',1,'2025-02-15 13:14:19.988622','2025-02-15 13:14:19.988622',0,1),(41,'DSC -> Uttara Metro rail Center -> Uttara Moylar Mor','R25',1,'2025-02-15 13:14:52.147731','2025-02-15 13:14:52.147731',1,0),(42,'Dhanmondi -> DSC','F1',1,'2025-02-15 13:15:34.930092','2025-02-15 13:15:34.930092',0,1),(43,'DSC -> Dhanmondi','F2',1,'2025-02-15 13:17:12.543609','2025-02-15 13:17:12.543609',1,0),(44,'Tongi College Gate -> Uttara -> DSC','F3',1,'2025-02-15 13:17:50.201187','2025-02-15 13:17:50.201187',0,1),(45,'DSC -> Uttara -> Tongi College Gate','F4',1,'2025-02-15 13:18:19.288213','2025-02-15 13:18:19.288213',1,0),(46,'Uttara - Rajlokkhi -> Uttara Metro rail Center -> DSC','F5',1,'2025-02-15 13:18:57.628840','2025-02-15 13:19:52.858140',0,1),(47,'DSC -> Uttara Metro rail Center -> Uttara - Rajlokkhi','F6',1,'2025-02-15 13:20:01.106474','2025-02-15 13:20:01.106474',1,0),(48,'Savar -> Nabinagar -> C&B -> DSC','F7',1,'2025-02-15 13:21:25.271289','2025-02-15 13:21:25.271289',0,1),(49,'DSC -> C&B -> Nabinagar -> Savar','F8',1,'2025-02-15 13:23:00.996618','2025-02-15 13:23:00.996618',1,0),(50,'Mirpur-10 -> Sony Cinema Hall -> DSC','F9',1,'2025-02-15 13:23:40.846421','2025-02-15 13:24:18.326364',0,1),(51,'DSC -> Sony Cinema Hall -> Mirpur-10','F10',1,'2025-02-15 13:24:05.540670','2025-02-15 13:24:05.540670',1,0);
/*!40000 ALTER TABLE `transit_hub_route` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `transit_hub_routestoppage`
--

DROP TABLE IF EXISTS `transit_hub_routestoppage`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `transit_hub_routestoppage` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) DEFAULT NULL,
  `route_id` bigint NOT NULL,
  `stoppage_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `transit_hub_routesto_stoppage_id_6400db9e_fk_transit_h` (`stoppage_id`),
  KEY `transit_hub_routestoppage_route_id_56efa909` (`route_id`),
  CONSTRAINT `transit_hub_routesto_route_id_56efa909_fk_transit_h` FOREIGN KEY (`route_id`) REFERENCES `transit_hub_route` (`id`),
  CONSTRAINT `transit_hub_routesto_stoppage_id_6400db9e_fk_transit_h` FOREIGN KEY (`stoppage_id`) REFERENCES `transit_hub_stoppage` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=424 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `transit_hub_routestoppage`
--

LOCK TABLES `transit_hub_routestoppage` WRITE;
/*!40000 ALTER TABLE `transit_hub_routestoppage` DISABLE KEYS */;
INSERT INTO `transit_hub_routestoppage` VALUES (131,'2025-02-15 09:48:41.515408',13,19),(132,'2025-02-15 09:48:41.515408',13,66),(133,'2025-02-15 09:48:41.515408',13,69),(134,'2025-02-15 09:48:41.515408',13,45),(135,'2025-02-15 09:48:41.515408',13,40),(136,'2025-02-15 09:48:41.515408',13,23),(137,'2025-02-15 09:48:41.515408',13,62),(138,'2025-02-15 09:48:41.515408',13,11),(139,'2025-02-15 09:48:41.515408',13,17),(140,'2025-02-15 09:49:20.649006',14,17),(141,'2025-02-15 09:49:20.649006',14,11),(142,'2025-02-15 09:49:20.649006',14,62),(143,'2025-02-15 09:49:20.649006',14,23),(144,'2025-02-15 09:49:20.649006',14,40),(145,'2025-02-15 09:49:20.649006',14,45),(146,'2025-02-15 09:49:20.649006',14,69),(147,'2025-02-15 09:49:20.649006',14,66),(148,'2025-02-15 09:49:20.649006',14,19),(149,'2025-02-15 09:50:17.484522',15,72),(150,'2025-02-15 09:50:17.484522',15,31),(151,'2025-02-15 09:50:17.484522',15,27),(152,'2025-02-15 09:50:17.484522',15,73),(153,'2025-02-15 09:50:17.484522',15,21),(154,'2025-02-15 09:50:17.484522',15,8),(155,'2025-02-15 09:50:17.484522',15,10),(156,'2025-02-15 09:50:17.484522',15,76),(157,'2025-02-15 09:50:17.484522',15,17),(158,'2025-02-15 09:50:58.470970',16,17),(159,'2025-02-15 09:50:58.470970',16,76),(160,'2025-02-15 09:50:58.470970',16,10),(161,'2025-02-15 09:50:58.470970',16,8),(162,'2025-02-15 09:50:58.470970',16,21),(163,'2025-02-15 09:50:58.470970',16,73),(164,'2025-02-15 09:50:58.470970',16,27),(165,'2025-02-15 09:50:58.470970',16,31),(166,'2025-02-15 09:50:58.470970',16,72),(167,'2025-02-15 09:52:18.538785',17,70),(168,'2025-02-15 09:52:18.538785',17,36),(169,'2025-02-15 09:52:18.538785',17,20),(170,'2025-02-15 09:52:18.538785',17,10),(171,'2025-02-15 09:52:18.538785',17,17),(172,'2025-02-15 09:52:49.889779',18,17),(173,'2025-02-15 09:52:49.889779',18,10),(174,'2025-02-15 09:52:49.889779',18,20),(175,'2025-02-15 09:52:49.889779',18,36),(176,'2025-02-15 09:52:49.889779',18,70),(177,'2025-02-15 09:53:35.093172',19,22),(178,'2025-02-15 09:53:35.093172',19,35),(179,'2025-02-15 09:53:35.093172',19,49),(180,'2025-02-15 09:53:35.093172',19,48),(181,'2025-02-15 09:53:35.093172',19,47),(182,'2025-02-15 09:53:35.093172',19,46),(183,'2025-02-15 09:53:35.093172',19,16),(184,'2025-02-15 09:53:35.093172',19,29),(185,'2025-02-15 09:53:35.093172',19,8),(186,'2025-02-15 09:53:35.093172',19,77),(187,'2025-02-15 09:53:35.093172',19,10),(188,'2025-02-15 09:53:35.093172',19,2),(189,'2025-02-15 09:53:35.093172',19,17),(190,'2025-02-15 09:54:32.838425',20,17),(191,'2025-02-15 09:54:32.838425',20,2),(192,'2025-02-15 09:54:32.838425',20,10),(193,'2025-02-15 09:54:32.838425',20,77),(194,'2025-02-15 09:54:32.838425',20,8),(195,'2025-02-15 09:54:32.838425',20,29),(196,'2025-02-15 09:54:32.838425',20,16),(197,'2025-02-15 09:54:32.838425',20,46),(198,'2025-02-15 09:54:32.838425',20,47),(199,'2025-02-15 09:54:32.838425',20,48),(200,'2025-02-15 09:54:32.838425',20,49),(201,'2025-02-15 09:54:32.838425',20,35),(202,'2025-02-15 09:54:32.838425',20,22),(203,'2025-02-15 09:55:55.855937',21,41),(204,'2025-02-15 09:55:55.855937',21,56),(205,'2025-02-15 09:55:55.855937',21,25),(206,'2025-02-15 09:55:55.855937',21,75),(207,'2025-02-15 09:55:55.855937',21,4),(208,'2025-02-15 09:55:55.855937',21,57),(209,'2025-02-15 09:55:55.855937',21,17),(210,'2025-02-15 09:56:46.875992',22,17),(211,'2025-02-15 09:56:46.875992',22,57),(212,'2025-02-15 09:56:46.875992',22,4),(213,'2025-02-15 09:56:46.875992',22,75),(214,'2025-02-15 09:56:46.875992',22,25),(215,'2025-02-15 09:56:46.875992',22,56),(216,'2025-02-15 09:56:46.875992',22,41),(217,'2025-02-15 09:57:30.882883',23,6),(218,'2025-02-15 09:57:30.882883',23,58),(219,'2025-02-15 09:57:30.882883',23,51),(220,'2025-02-15 09:57:30.882883',23,9),(221,'2025-02-15 09:57:30.882883',23,59),(222,'2025-02-15 09:57:30.882883',23,33),(223,'2025-02-15 09:57:30.882883',23,13),(224,'2025-02-15 09:57:30.882883',23,39),(225,'2025-02-15 09:57:30.882883',23,14),(226,'2025-02-15 09:57:30.882883',23,42),(227,'2025-02-15 09:57:30.882883',23,17),(228,'2025-02-15 09:58:25.637702',24,17),(229,'2025-02-15 09:58:25.637702',24,42),(230,'2025-02-15 09:58:25.637702',24,14),(231,'2025-02-15 09:58:25.637702',24,39),(232,'2025-02-15 09:58:25.637702',24,13),(233,'2025-02-15 09:58:25.637702',24,33),(234,'2025-02-15 09:58:25.637702',24,59),(235,'2025-02-15 09:58:25.637702',24,9),(236,'2025-02-15 09:58:25.637702',24,51),(237,'2025-02-15 09:58:25.637702',24,58),(238,'2025-02-15 09:58:25.637702',24,6),(239,'2025-02-15 09:59:24.528665',25,18),(240,'2025-02-15 09:59:24.528665',25,37),(241,'2025-02-15 09:59:24.528665',25,26),(242,'2025-02-15 09:59:24.528665',25,51),(243,'2025-02-15 09:59:24.528665',25,9),(244,'2025-02-15 09:59:24.528665',25,59),(245,'2025-02-15 09:59:24.528665',25,33),(246,'2025-02-15 09:59:24.528665',25,13),(247,'2025-02-15 09:59:24.528665',25,39),(248,'2025-02-15 09:59:24.528665',25,14),(249,'2025-02-15 09:59:24.528665',25,42),(250,'2025-02-15 09:59:24.528665',25,17),(251,'2025-02-15 10:01:54.484931',26,17),(252,'2025-02-15 10:01:54.484931',26,42),(253,'2025-02-15 10:01:54.484931',26,14),(254,'2025-02-15 10:01:54.484931',26,39),(255,'2025-02-15 10:01:54.484931',26,13),(256,'2025-02-15 10:01:54.484931',26,33),(257,'2025-02-15 10:01:54.484931',26,59),(258,'2025-02-15 10:01:54.484931',26,9),(259,'2025-02-15 10:01:54.484931',26,51),(260,'2025-02-15 10:01:54.484931',26,26),(261,'2025-02-15 10:01:54.484931',26,37),(262,'2025-02-15 10:01:54.484931',26,18),(263,'2025-02-15 10:28:47.555274',31,64),(264,'2025-02-15 10:28:47.555274',31,60),(265,'2025-02-15 10:28:47.555274',31,13),(266,'2025-02-15 10:28:47.555274',31,39),(267,'2025-02-15 10:28:47.555274',31,14),(268,'2025-02-15 10:28:47.555274',31,42),(269,'2025-02-15 10:28:47.555274',31,17),(270,'2025-02-15 10:29:26.872326',32,17),(271,'2025-02-15 10:29:26.872326',32,42),(272,'2025-02-15 10:29:26.872326',32,14),(273,'2025-02-15 10:29:26.872326',32,39),(274,'2025-02-15 10:29:26.872326',32,13),(275,'2025-02-15 10:29:26.872326',32,60),(276,'2025-02-15 10:29:26.872326',32,64),(277,'2025-02-15 10:38:37.640105',33,52),(278,'2025-02-15 10:38:37.640105',33,67),(279,'2025-02-15 10:38:37.640105',33,78),(280,'2025-02-15 10:38:37.640105',33,65),(281,'2025-02-15 10:38:37.640105',33,30),(282,'2025-02-15 10:38:37.640105',33,15),(283,'2025-02-15 10:38:37.640105',33,54),(284,'2025-02-15 10:38:37.640105',33,53),(285,'2025-02-15 10:38:37.640105',33,38),(286,'2025-02-15 10:38:37.640105',33,19),(287,'2025-02-15 10:38:37.640105',33,66),(288,'2025-02-15 10:38:37.640105',33,69),(289,'2025-02-15 10:38:37.640105',33,45),(290,'2025-02-15 10:38:37.640105',33,40),(291,'2025-02-15 10:38:37.640105',33,24),(292,'2025-02-15 10:38:37.640105',33,11),(293,'2025-02-15 10:38:37.640105',33,17),(294,'2025-02-15 10:40:19.306001',34,28),(295,'2025-02-15 10:40:19.306001',34,79),(296,'2025-02-15 10:40:19.306001',34,44),(297,'2025-02-15 10:40:19.306001',34,61),(298,'2025-02-15 10:40:19.306001',34,12),(299,'2025-02-15 10:40:19.306001',34,1),(300,'2025-02-15 10:40:19.306001',34,5),(301,'2025-02-15 10:40:19.306001',34,32),(302,'2025-02-15 10:40:19.306001',34,80),(303,'2025-02-15 10:40:19.306001',34,43),(304,'2025-02-15 10:40:19.306001',34,72),(305,'2025-02-15 10:40:19.306001',34,31),(306,'2025-02-15 10:40:19.306001',34,21),(307,'2025-02-15 10:40:19.306001',34,8),(308,'2025-02-15 10:40:19.306001',34,10),(309,'2025-02-15 10:40:19.306001',34,76),(310,'2025-02-15 10:40:19.306001',34,3),(311,'2025-02-15 10:40:19.306001',34,17),(312,'2025-02-15 10:40:58.877248',35,17),(313,'2025-02-15 10:40:58.877248',35,3),(314,'2025-02-15 10:40:58.877248',35,76),(315,'2025-02-15 10:40:58.877248',35,10),(316,'2025-02-15 10:40:58.877248',35,8),(317,'2025-02-15 10:40:58.877248',35,21),(318,'2025-02-15 10:40:58.877248',35,31),(319,'2025-02-15 10:40:58.877248',35,72),(320,'2025-02-15 10:40:58.877248',35,43),(321,'2025-02-15 10:40:58.877248',35,80),(322,'2025-02-15 10:40:58.877248',35,32),(323,'2025-02-15 10:40:58.877248',35,5),(324,'2025-02-15 10:40:58.877248',35,1),(325,'2025-02-15 10:40:58.877248',35,12),(326,'2025-02-15 10:40:58.877248',35,61),(327,'2025-02-15 10:40:58.877248',35,44),(328,'2025-02-15 10:40:58.877248',35,79),(329,'2025-02-15 10:40:58.877248',35,28),(330,'2025-02-15 13:08:31.814030',36,71),(331,'2025-02-15 13:08:31.815009',36,36),(332,'2025-02-15 13:08:31.815647',36,20),(333,'2025-02-15 13:08:31.815647',36,10),(334,'2025-02-15 13:08:31.815647',36,17),(335,'2025-02-15 13:10:33.943036',37,17),(336,'2025-02-15 13:10:33.943036',37,10),(337,'2025-02-15 13:10:33.943036',37,20),(338,'2025-02-15 13:10:33.943036',37,36),(339,'2025-02-15 13:10:33.943036',37,71),(340,'2025-02-15 13:11:34.895038',38,68),(341,'2025-02-15 13:11:34.895038',38,29),(342,'2025-02-15 13:11:34.895038',38,8),(343,'2025-02-15 13:11:34.895038',38,23),(344,'2025-02-15 13:11:34.895038',38,10),(345,'2025-02-15 13:11:34.895038',38,2),(346,'2025-02-15 13:11:34.895038',38,17),(347,'2025-02-15 13:12:58.033394',39,17),(348,'2025-02-15 13:12:58.033394',39,2),(349,'2025-02-15 13:12:58.033394',39,10),(350,'2025-02-15 13:12:58.033394',39,23),(351,'2025-02-15 13:12:58.033394',39,8),(352,'2025-02-15 13:12:58.033394',39,29),(353,'2025-02-15 13:12:58.033394',39,68),(354,'2025-02-15 13:14:19.988622',40,74),(355,'2025-02-15 13:14:19.988622',40,73),(356,'2025-02-15 13:14:19.988622',40,8),(357,'2025-02-15 13:14:19.988622',40,10),(358,'2025-02-15 13:14:19.988622',40,76),(359,'2025-02-15 13:14:19.988622',40,17),(360,'2025-02-15 13:14:52.150682',41,17),(361,'2025-02-15 13:14:52.150682',41,76),(362,'2025-02-15 13:14:52.150682',41,10),(363,'2025-02-15 13:14:52.150682',41,8),(364,'2025-02-15 13:14:52.150682',41,73),(365,'2025-02-15 13:14:52.150682',41,74),(366,'2025-02-15 13:16:29.753289',42,19),(367,'2025-02-15 13:16:29.753289',42,66),(368,'2025-02-15 13:16:29.753289',42,69),(369,'2025-02-15 13:16:29.753289',42,45),(370,'2025-02-15 13:16:29.753289',42,50),(371,'2025-02-15 13:16:29.753289',42,24),(372,'2025-02-15 13:16:29.753289',42,11),(373,'2025-02-15 13:16:29.753289',42,17),(374,'2025-02-15 13:17:12.557631',43,17),(375,'2025-02-15 13:17:12.557631',43,11),(376,'2025-02-15 13:17:12.557631',43,24),(377,'2025-02-15 13:17:12.557631',43,50),(378,'2025-02-15 13:17:12.557631',43,45),(379,'2025-02-15 13:17:12.557631',43,69),(380,'2025-02-15 13:17:12.557631',43,66),(381,'2025-02-15 13:17:12.557631',43,19),(382,'2025-02-15 13:17:50.207931',44,70),(383,'2025-02-15 13:17:50.207931',44,36),(384,'2025-02-15 13:17:50.207931',44,20),(385,'2025-02-15 13:17:50.207931',44,10),(386,'2025-02-15 13:17:50.207931',44,17),(387,'2025-02-15 13:18:19.301770',45,17),(388,'2025-02-15 13:18:19.301770',45,10),(389,'2025-02-15 13:18:19.301770',45,20),(390,'2025-02-15 13:18:19.301770',45,36),(391,'2025-02-15 13:18:19.301770',45,70),(392,'2025-02-15 13:18:57.628840',46,72),(393,'2025-02-15 13:18:57.628840',46,31),(394,'2025-02-15 13:18:57.628840',46,27),(395,'2025-02-15 13:18:57.628840',46,73),(396,'2025-02-15 13:18:57.628840',46,21),(397,'2025-02-15 13:18:57.628840',46,8),(398,'2025-02-15 13:18:57.628840',46,10),(399,'2025-02-15 13:18:57.628840',46,76),(400,'2025-02-15 13:18:57.628840',46,17),(401,'2025-02-15 13:20:01.116278',47,17),(402,'2025-02-15 13:20:01.116278',47,76),(403,'2025-02-15 13:20:01.116278',47,10),(404,'2025-02-15 13:20:01.116278',47,8),(405,'2025-02-15 13:20:01.116278',47,21),(406,'2025-02-15 13:20:01.116278',47,73),(407,'2025-02-15 13:20:01.116278',47,27),(408,'2025-02-15 13:20:01.116278',47,31),(409,'2025-02-15 13:20:01.116278',47,72),(410,'2025-02-15 13:21:25.280125',48,63),(411,'2025-02-15 13:21:25.280125',48,55),(412,'2025-02-15 13:21:25.280125',48,13),(413,'2025-02-15 13:21:25.280125',48,81),(414,'2025-02-15 13:23:01.003747',49,17),(415,'2025-02-15 13:23:01.003747',49,13),(416,'2025-02-15 13:23:01.003747',49,55),(417,'2025-02-15 13:23:01.003747',49,63),(418,'2025-02-15 13:23:40.876328',50,82),(419,'2025-02-15 13:23:40.876328',50,68),(420,'2025-02-15 13:23:40.876328',50,17),(421,'2025-02-15 13:24:05.553699',51,17),(422,'2025-02-15 13:24:05.553699',51,68),(423,'2025-02-15 13:24:05.553699',51,82);
/*!40000 ALTER TABLE `transit_hub_routestoppage` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `transit_hub_stoppage`
--

DROP TABLE IF EXISTS `transit_hub_stoppage`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `transit_hub_stoppage` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `stoppage_name` varchar(100) NOT NULL,
  `stoppage_status` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `stoppage_name` (`stoppage_name`)
) ENGINE=InnoDB AUTO_INCREMENT=83 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `transit_hub_stoppage`
--

LOCK TABLES `transit_hub_stoppage` WRITE;
/*!40000 ALTER TABLE `transit_hub_stoppage` DISABLE KEYS */;
INSERT INTO `transit_hub_stoppage` VALUES (1,'Aftabnagar',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(2,'Akran',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(3,'Akran Bazaar Bus Stand',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(4,'Ashulia Bazar',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(5,'Badda Suvastu tower',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(6,'Baipail',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(7,'Basabo',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(8,'Beribadh',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(9,'Bismail',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(10,'Birulia',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(11,'Birulia Bus Stand',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(12,'BTV Center',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(13,'C&B',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(14,'Charabag',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(15,'Chankharpul',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(16,'Commerce College',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(17,'Daffodil Smart City',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(18,'Dhamrai Bus Stand',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(19,'Dhanmondi - Sobhanbag',1,'2025-02-15 07:10:22.014744','2025-02-15 07:11:13.132912'),(20,'Dhour',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(21,'Diyabari Bridge',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(22,'ECB Chattor',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(23,'Eastern Housing',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(24,'Eastern Housing Rup Nogor',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(25,'Ghosbag',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(26,'Gonosastho',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(27,'Grand Zamzam Tower',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(28,'Green Model Town',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(29,'Gudaraghat',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(30,'Gulistan',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(31,'House building',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(32,'Jamuna Future Park',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(33,'JU',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(34,'Kajla',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(35,'Kalshi More',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(36,'Kamar Para',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(37,'Kohinur Market',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(38,'Kolabagan',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(39,'Kolma',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(40,'Konabari Bus Stop',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(41,'Konabari Pukur Par',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(42,'Kumkumari',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(43,'Khilkhet',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(44,'Malibagh Railgate South Bus Stop',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(45,'Majar Road Gabtoli',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(46,'Mirpur 01 - Sony Cinema Hall',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(47,'Mirpur 02',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(48,'Mirpur 10',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(49,'Mirpur 12',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(50,'Mirpur Konabari',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(51,'Nabinagar',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(52,'Narayanganj Chasara',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(53,'New Market',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(54,'Nilkhet',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(55,'Nobinagar',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(56,'Norshingpur',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(57,'Paragram',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(58,'Polli Biddut',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(59,'Prantik',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(60,'Radio Colony',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(61,'Rampura Bazaar Bus Stop',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(62,'Rupnagar',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(63,'Savar',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(64,'Savar Bus Stand',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(65,'Saydabad Bus Stand',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(66,'Shyamoli Square',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(67,'Sign board',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(68,'Sony Cinema Hall',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(69,'Technical Mor',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(70,'Tongi College Gate Bus Stand',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(71,'Tongi Station Route',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(72,'Uttara - Rajlokkhi',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(73,'Uttara Metro Rail Center',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(74,'Uttara Moylar Mor',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(75,'Zirabo',1,'2025-02-15 07:10:22.014744','2025-02-15 07:10:22.014744'),(76,'Khagan',1,'2025-02-15 09:50:17.466241','2025-02-15 09:50:17.466241'),(77,'Estern Housing',1,'2025-02-15 09:53:35.072496','2025-02-15 09:53:35.072496'),(78,'Sonir Akhra',1,'2025-02-15 10:38:37.626182','2025-02-15 10:38:37.626182'),(79,'Bashabo',1,'2025-02-15 10:40:19.263527','2025-02-15 10:40:19.263527'),(80,'Kuril Bisso Road',1,'2025-02-15 10:40:19.295061','2025-02-15 10:40:19.295061'),(81,'DSC',1,'2025-02-15 13:21:25.256167','2025-02-15 13:21:25.256167'),(82,'Mirpur-10',1,'2025-02-15 13:23:40.803657','2025-02-15 13:23:40.803657');
/*!40000 ALTER TABLE `transit_hub_stoppage` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `transport_manager_transportation_schedules`
--

DROP TABLE IF EXISTS `transport_manager_transportation_schedules`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `transport_manager_transportation_schedules` (
  `schedule_id` int NOT NULL AUTO_INCREMENT,
  `departure_time` time(6) NOT NULL,
  `schedule_status` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `bus_id` bigint NOT NULL,
  `driver_id` bigint NOT NULL,
  `route_id` bigint NOT NULL,
  `audience` varchar(20) NOT NULL,
  `from_dsc` tinyint(1) NOT NULL,
  `to_dsc` tinyint(1) NOT NULL,
  `days` varchar(56) NOT NULL,
  PRIMARY KEY (`schedule_id`),
  UNIQUE KEY `transport_manager_transp_schedule_id_route_id_bus_c4cb6d8f_uniq` (`schedule_id`,`route_id`,`bus_id`,`driver_id`),
  KEY `transport_manager_tr_bus_id_2b6f28af_fk_transit_h` (`bus_id`),
  KEY `transport_manager_tr_driver_id_ee14fd5d_fk_transit_h` (`driver_id`),
  KEY `transport_manager_tr_route_id_22603e8a_fk_transit_h` (`route_id`),
  CONSTRAINT `transport_manager_tr_bus_id_2b6f28af_fk_transit_h` FOREIGN KEY (`bus_id`) REFERENCES `transit_hub_bus` (`id`),
  CONSTRAINT `transport_manager_tr_driver_id_ee14fd5d_fk_transit_h` FOREIGN KEY (`driver_id`) REFERENCES `transit_hub_driver` (`id`),
  CONSTRAINT `transport_manager_tr_route_id_22603e8a_fk_transit_h` FOREIGN KEY (`route_id`) REFERENCES `transit_hub_route` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `transport_manager_transportation_schedules`
--

LOCK TABLES `transport_manager_transportation_schedules` WRITE;
/*!40000 ALTER TABLE `transport_manager_transportation_schedules` DISABLE KEYS */;
INSERT INTO `transport_manager_transportation_schedules` VALUES (1,'16:52:34.000000',1,'2025-05-18 16:52:39.270252',1,1,13,'student',0,1,'monday,tuesday,wednesday,thursday,saturday,sunday'),(2,'16:52:59.000000',1,'2025-05-18 16:53:03.419198',2,2,15,'student',0,1,'monday,tuesday,wednesday,thursday,saturday,sunday'),(3,'17:16:16.000000',0,'2025-05-20 06:16:20.127859',2,1,16,'female_only',1,0,'monday,tuesday,wednesday,thursday,saturday,sunday'),(4,'16:17:09.000000',0,'2025-05-20 06:17:11.756748',1,2,15,'employee',0,1,'monday,tuesday,wednesday,thursday,friday,saturday,sunday'),(5,'13:17:19.000000',0,'2025-05-20 06:17:21.308087',2,2,15,'female_only',0,1,'monday,tuesday,wednesday,thursday,friday,saturday,sunday'),(6,'23:36:54.000000',1,'2025-06-03 10:36:58.177396',1,1,20,'student',1,0,'monday,tuesday,wednesday,thursday,friday,saturday,sunday'),(7,'23:40:05.000000',1,'2025-06-03 10:38:03.121040',2,1,16,'student',1,0,'monday,tuesday,wednesday,thursday,friday,saturday,sunday'),(8,'10:38:19.000000',1,'2025-06-03 10:38:23.059058',1,2,19,'student',0,1,'tuesday,wednesday,thursday,friday,saturday,sunday'),(9,'10:38:36.000000',1,'2025-06-03 10:38:42.171453',2,2,13,'student',0,1,'[]'),(11,'23:30:00.000000',1,'2025-06-05 09:01:38.710276',1,2,14,'student',1,0,'monday,tuesday,wednesday,thursday,friday,saturday,sunday');
/*!40000 ALTER TABLE `transport_manager_transportation_schedules` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-06-17 23:53:07
