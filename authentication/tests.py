from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages
from authentication.models import Student


class AuthenticationTestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.student = Student.objects.create(
            student_id="TEST001",
            name="Test Student",
            email="test@example.com",
            phone_number="1234567890",
            verified=True,
        )
        self.student.set_password("testpassword123")
        self.student.save()

    def test_login_with_correct_credentials(self):
        """Test successful login with correct credentials"""
        response = self.client.post(
            reverse("login_request"),
            {"student_id": "TEST001", "password": "testpassword123"},
        )

        # Should redirect to index
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("index"))

        # Check session is set
        self.assertEqual(self.client.session.get("username"), self.student.username)
        self.assertTrue(self.client.session.get("is_student_authenticated"))

    def test_login_with_wrong_password(self):
        """Test login failure with wrong password"""
        response = self.client.post(
            reverse("login_request"),
            {"student_id": "TEST001", "password": "wrongpassword"},
        )

        # Should redirect to index
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("index"))

        # Check session is not set
        self.assertNotIn("username", self.client.session)
        self.assertNotIn("is_student_authenticated", self.client.session)

        # Check error message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any("Incorrect password" in str(message) for message in messages)
        )

    def test_login_with_nonexistent_student(self):
        """Test login failure with non-existent student ID"""
        response = self.client.post(
            reverse("login_request"),
            {"student_id": "NONEXISTENT", "password": "somepassword"},
        )

        # Should redirect to index
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("index"))

        # Check session is not set
        self.assertNotIn("username", self.client.session)
        self.assertNotIn("is_student_authenticated", self.client.session)

        # Check error message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any("Student ID not found" in str(message) for message in messages)
        )

    def test_login_with_empty_credentials(self):
        """Test login failure with empty credentials"""
        response = self.client.post(
            reverse("login_request"), {"student_id": "", "password": ""}
        )

        # Should redirect to index
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("index"))

        # Check error message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(
                "Please provide both Student ID and password" in str(message)
                for message in messages
            )
        )

    def test_login_with_unverified_student(self):
        """Test login failure with unverified student"""
        # Create unverified student
        unverified_student = Student.objects.create(
            student_id="UNVERIFIED001",
            name="Unverified Student",
            email="unverified@example.com",
            phone_number="9876543210",
            verified=False,
        )
        unverified_student.set_password("testpassword123")
        unverified_student.save()

        response = self.client.post(
            reverse("login_request"),
            {"student_id": "UNVERIFIED001", "password": "testpassword123"},
        )

        # Should redirect to index
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("index"))

        # Check session is not set
        self.assertNotIn("username", self.client.session)
        self.assertNotIn("is_student_authenticated", self.client.session)

        # Check error message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("not verified" in str(message) for message in messages))

    def test_register_with_valid_data(self):
        """Test successful registration with valid data"""
        response = self.client.post(
            reverse("register"),
            {
                "student_id": "NEW001",
                "name": "New Student",
                "email": "new@example.com",
                "phone_number": "5555555555",
                "password": "newpassword123",
            },
        )

        # Should redirect to verify_otp
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("verify_otp"))

        # Check student was created
        new_student = Student.objects.get(student_id="NEW001")
        self.assertEqual(new_student.name, "New Student")
        self.assertEqual(new_student.email, "new@example.com")
        self.assertFalse(new_student.verified)  # Should be unverified initially

    def test_register_with_existing_student_id(self):
        """Test registration failure with existing student ID"""
        response = self.client.post(
            reverse("register"),
            {
                "student_id": "TEST001",  # Already exists
                "name": "Another Student",
                "email": "another@example.com",
                "phone_number": "7777777777",
                "password": "anotherpassword123",
            },
        )

        # Should redirect to index
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("index"))

        # Check error message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any("Student ID already exists" in str(message) for message in messages)
        )

    def test_register_with_short_password(self):
        """Test registration failure with short password"""
        response = self.client.post(
            reverse("register"),
            {
                "student_id": "SHORT001",
                "name": "Short Password Student",
                "email": "short@example.com",
                "phone_number": "8888888888",
                "password": "123",  # Too short
            },
        )

        # Should redirect to index
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("index"))

        # Check error message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any("at least 6 characters" in str(message) for message in messages)
        )

    def test_resend_otp_success(self):
        """Test successful OTP resend"""
        # Create unverified student and set session
        unverified_student = Student.objects.create(
            student_id="RESEND001",
            name="Resend Student",
            email="resend@example.com",
            phone_number="9999999999",
            verified=False,
        )
        unverified_student.set_password("testpassword123")
        unverified_student.save()

        # Set session to simulate logged in unverified user
        session = self.client.session
        session["username"] = unverified_student.username
        session.save()

        response = self.client.post(reverse("resend_otp"))

        # Should return success JSON response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIn("sent to your email", data["message"])

    def test_resend_otp_no_session(self):
        """Test OTP resend failure without session"""
        response = self.client.post(reverse("resend_otp"))

        # Should return error JSON response
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertIn("Session expired", data["message"])
