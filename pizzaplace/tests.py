from django.test import TestCase
from pizzaplace.models import PizzaPlace
from pizzaplace.services.pizza_place_presenter import PizzaPlacePresenter 
from django.db import IntegrityError
from django.db import DataError
from django.core.exceptions import ValidationError
from unittest import mock
from unittest.mock import patch
from pizzaplace.services.yelp_api import YelpApi

class TestPizzaPlace(TestCase):

  def setUp(self):
    self.prince_street_pizza_link = 'https://www.yelp.com/biz/prince-st-pizza-new-york'
    self.pizza_name1 = 'Such Pizza'

  def test_pizza_is_real(self):
    pizza_place = PizzaPlace()
    self.assertIsInstance(pizza_place, PizzaPlace)

  def test_creation_of_pizza_place_with_name(self):
    pizza_place = PizzaPlace(name=self.pizza_name1, yelp_link=self.prince_street_pizza_link)
    self.assertEquals(pizza_place.name, self.pizza_name1)

  def test_name_must_be_unique(self):
    place1 = PizzaPlace.objects.create(name=self.pizza_name1, yelp_link=self.prince_street_pizza_link)
    place2 = PizzaPlace(name=self.pizza_name1, yelp_link='https://www.yelp.com/biz/lombardis-pizza-new-york')
    self.assertRaises(IntegrityError, place2.save)

  def test_link_must_be_unique(self):
    place1 = PizzaPlace.objects.create(name="Much Pizza", yelp_link=self.prince_street_pizza_link)
    place2 = PizzaPlace(name=self.pizza_name1, yelp_link=self.prince_street_pizza_link)
    self.assertRaises(IntegrityError, place2.save)

  def test_string_representation_of_pizza_place(self):
    place = PizzaPlace(name=self.pizza_name1, yelp_link=self.prince_street_pizza_link)
    self.assertEquals(self.pizza_name1, str(place))

  def test_name_length_invalid_if_over_500_char(self):
    name = "x" * 501
    place = PizzaPlace(name=name, yelp_link=self.prince_street_pizza_link)
    self.assertRaises(DataError, place.save)

  def test_raises_error_if_name_is_blank(self):
    place = PizzaPlace(yelp_link=self.prince_street_pizza_link)
    self.assertRaises(IntegrityError, place.save)

  def test_raises_error_if_link_is_blank(self):
    place = PizzaPlace(name=self.pizza_name1)
    self.assertRaises(IntegrityError, place.save)


class TestPizzaPlaceModelValidations(TestCase):

  def test_error_raised_on_nonsense_url(self):
    pizza_place = PizzaPlace(name="Name", yelp_link="not.a/link?")
    self.assertRaises(ValidationError, pizza_place.full_clean)

  def test_error_raised_if_not_a_yelp_link(self):
    pizza_place = PizzaPlace(name="Name", yelp_link="http://notyelpatall.com/biz/prince-st-pizza-new-york")
    self.assertRaises(ValidationError, pizza_place.full_clean)
  
  def test_error_raised_if_no_bizname_in_pizza_place_url(self):
    pizza_place = PizzaPlace(name="Oh Pizza!", yelp_link='https://www.yelp.com/biz/')
    self.assertRaises(ValidationError, pizza_place.full_clean)  

  def test_error_raised_if_no_biz_key_in_pizza_place_url(self):
    pizza_place = PizzaPlace(name="Oh Pizza!", yelp_link='https://www.yelp.com/prince-st-pizza-new-york')
    self.assertRaises(ValidationError, pizza_place.full_clean)

  def test_no_error_raised_if_link_contains_search_query_params(self):
    pizza_place = PizzaPlace(name="Oh Pizza!", yelp_link='https://www.yelp.com/biz/lombardis-pizza-new-york?osq=lombardis-pizza-new-york')
    errors_raised_by_pizza_place = pizza_place.full_clean()
    self.assertIsNone(errors_raised_by_pizza_place)
    
  def test_error_raised_if_link_doesnt_contain_valid_business_name(self):
    pizza_place = PizzaPlace(name="Oh Pizza!", yelp_link='https://www.yelp.com/biz/imaginary-pizza/')
    self.assertRaises(ValidationError, pizza_place.full_clean)

  def test_no_error_raised_if_link_contains_no_search_query_params(self):
    pizza_place = PizzaPlace(name="Oh Pizza!", yelp_link='https://www.yelp.com/biz/lombardis-pizza-new-york')
    errors_raised_by_pizza_place = pizza_place.full_clean()
    self.assertIsNone(errors_raised_by_pizza_place)

  def test_error_raised_if_link_has_multiple_biznames(self):
    pizza_place = PizzaPlace(name="Oh Pizza!", yelp_link='https://www.yelp.com/biz/lombardis-pizza-new-york/some-other-stuff')
    self.assertRaises(ValidationError, pizza_place.full_clean)

class TestPizzaPlacePresenter(TestCase):

  def setUp(self):
    self.patcher = patch('pizzaplace.services.yelp_api')
    self.mock_yelp_api = self.patcher.start()
    self.mock_yelp_api.return_value.get_response.return_value.json.return_value = {'rating' : 5}
    self.pizza_place = PizzaPlace(name='Oh Pizza!', yelp_link='https://www.yelp.com/biz/lombardis-pizza-new-york')

  def test_yelp_presenter_returns_yelp_link(self):
    presenter = PizzaPlacePresenter(self.pizza_place, self.mock_yelp_api)
    self.assertEquals(presenter.get_yelp_link(), 'https://www.yelp.com/biz/lombardis-pizza-new-york')

  def test_yelp_presenter_returns_business_name(self):
    presenter = PizzaPlacePresenter(self.pizza_place, self.mock_yelp_api)
    self.assertEquals(presenter.get_pizza_place_name(), 'Oh Pizza!')

  def test_yelp_presenter_returns_yelp_review(self):
    presenter = PizzaPlacePresenter(self.pizza_place, self.mock_yelp_api)
    self.assertEquals(presenter.get_pizza_place_rating(), "🍕🍕🍕🍕🍕")

  def test_yelp_presenter_rounds_yelp_review_down(self):
    self.mock_yelp_api.return_value.get_response.return_value.json.return_value = {'rating' : 4.5}
    presenter = PizzaPlacePresenter(self.pizza_place, self.mock_yelp_api)
    self.assertEquals(presenter.get_pizza_place_rating(), "🍕🍕🍕🍕")
  
  def test_yelp_presenter_rounds_yelp_review_down(self):
    self.mock_yelp_api.return_value.get_response.return_value.json.return_value = {}
    presenter = PizzaPlacePresenter(self.pizza_place, self.mock_yelp_api)
    self.assertEquals(presenter.get_pizza_place_rating(), "No Rating")

  def tearDown(self):
    self.addCleanup(self.patcher.stop)


class TestYelpApi(TestCase):

  def test_can_parse_out_business_id(self):
    lookup_agent = YelpApi('https://www.yelp.com/biz/prince-st-pizza-new-york')
    business_id = lookup_agent.get_unique_id()
    self.assertEquals('prince-st-pizza-new-york', business_id)

  def test_can_parse_out_business_id_from_search_url(self):
    lookup_agent = YelpApi('https://www.yelp.com/biz/prince-st-pizza-new-york?osq=prince+street+pizza')
    business_id = lookup_agent.get_unique_id()
    self.assertEquals('prince-st-pizza-new-york', business_id)

  def test_invalid_link_returns_400(self):
    lookup_agent = YelpApi('https://www.yelp.com/biz/not-a-real-place')
    response = lookup_agent.get_response()
    self.assertEquals(400, response.status_code)

  def test_validator_returns_true_for_valid_url(self):
    lookup_agent = YelpApi("https://www.yelp.com/biz/prince-st-pizza-new-york")
    is_valid = lookup_agent.url_exists()
    self.assertTrue(is_valid)

  def test_validator_returns_false_for_invalid_url(self):
    lookup_agent = YelpApi("https://www.yelp.com/biz/this-is-not-a-meetup")
    is_valid = lookup_agent.url_exists()
    self.assertFalse(is_valid)