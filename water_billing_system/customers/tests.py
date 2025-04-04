from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Customer

User = get_user_model()

class CustomerTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.client.force_authenticate(user=self.user)
        
        self.customer_data = {
            'email': 'customer@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'phone_number': '+1234567890',
            'address': '123 Main St'
        }

    def test_create_customer(self):
        """Test creating a new customer"""
        response = self.client.post(
            reverse('customer-list'),
            self.customer_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Customer.objects.count(), 1)
        self.assertEqual(Customer.objects.get().email, 'customer@example.com')

    def test_retrieve_customer(self):
        """Test retrieving a customer"""
        customer = Customer.objects.create(**self.customer_data)
        response = self.client.get(
            reverse('customer-detail', args=[customer.id])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], customer.email)

    def test_update_customer(self):
        """Test updating a customer"""
        customer = Customer.objects.create(**self.customer_data)
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'phone_number': '+9876543210'
        }
        response = self.client.patch(
            reverse('customer-detail', args=[customer.id]),
            update_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        customer.refresh_from_db()
        self.assertEqual(customer.first_name, 'Updated')

    def test_delete_customer(self):
        """Test deleting a customer"""
        customer = Customer.objects.create(**self.customer_data)
        response = self.client.delete(
            reverse('customer-detail', args=[customer.id])
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Customer.objects.count(), 0)

    def test_list_customers(self):
        """Test listing all customers"""
        Customer.objects.create(**self.customer_data)
        Customer.objects.create(
            email='another@example.com',
            first_name='Jane',
            last_name='Smith',
            phone_number='+9876543210',
            address='456 Oak Ave'
        )
        
        response = self.client.get(reverse('customer-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_unauthorized_access(self):
        """Test unauthorized access to customer endpoints"""
        self.client.force_authenticate(user=None)
        response = self.client.get(reverse('customer-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
