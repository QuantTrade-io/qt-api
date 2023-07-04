import json

from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from qt_billing.factories import ProductUtilFactory


class ProductsAPITests(TestCase):
    """
    Test Products API
    """

    def test_get_product_utils_empty(self):
        """
        Should return 200 & empty list
        """
        url = self._get_url()

        response = self.client.get(url, format="json")
        parsed_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(parsed_response["products"], [])

    def test_get_product_utils_one_product_en(self):
        """
        Should return 200 & one Product with 3 EN unique selling points
        """
        product_util = ProductUtilFactory()

        url = self._get_url()

        response = self.client.get(url, format="json")
        parsed_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(parsed_response["products"]), 1)
        self.assertEqual(parsed_response["products"][0]["id"], product_util.product.id)
        self.assertEqual(
            parsed_response["products"][0]["name"], product_util.product.name
        )
        self.assertEqual(
            len(parsed_response["products"][0]["unique_selling_points"]), 3
        )
        self.assertEqual(
            parsed_response["products"][0]["unique_selling_points"][0]["description"],
            product_util.unique_selling_points.all()[0].description_en,
        )
        self.assertEqual(
            parsed_response["products"][0]["unique_selling_points"][1]["description"],
            product_util.unique_selling_points.all()[1].description_en,
        )
        self.assertEqual(
            parsed_response["products"][0]["unique_selling_points"][2]["description"],
            product_util.unique_selling_points.all()[2].description_en,
        )
        self.assertEqual(len(parsed_response["products"][0]["prices"]), 0)
        self.assertEqual(parsed_response["products"][0]["prices"], [])

    def test_get_product_utils_one_product_nl(self):
        """
        Should return 200 & one Product with 3 EN unique selling points
        """
        product_util = ProductUtilFactory()

        url = self._get_url()

        header = {"HTTP_ACCEPT_LANGUAGE": "nl-NL;q=1.0"}

        response = self.client.get(url, **header, format="json")
        parsed_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(parsed_response["products"]), 1)
        self.assertEqual(parsed_response["products"][0]["id"], product_util.product.id)
        self.assertEqual(
            parsed_response["products"][0]["name"], product_util.product.name
        )
        self.assertEqual(
            len(parsed_response["products"][0]["unique_selling_points"]), 3
        )
        self.assertEqual(
            parsed_response["products"][0]["unique_selling_points"][0]["description"],
            product_util.unique_selling_points.all()[0].description_nl,
        )
        self.assertEqual(
            parsed_response["products"][0]["unique_selling_points"][1]["description"],
            product_util.unique_selling_points.all()[1].description_nl,
        )
        self.assertEqual(
            parsed_response["products"][0]["unique_selling_points"][2]["description"],
            product_util.unique_selling_points.all()[2].description_nl,
        )
        self.assertEqual(len(parsed_response["products"][0]["prices"]), 0)
        self.assertEqual(parsed_response["products"][0]["prices"], [])

    def _get_url(self):
        return reverse("products")
