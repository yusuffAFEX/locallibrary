import uuid
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import date


# Create your models here.
class Genre(models.Model):
    name = models.CharField(max_length=200, help_text='Enter a book genre (e.g Science Fiction)')

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)
    summary = models.TextField(max_length=1000, help_text='Enter brief description of the book.')
    isbn = models.CharField('ISBN', max_length=13, unique=True,
                            help_text='13 Character, <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>')
    genre = models.ManyToManyField(Genre, help_text='Select a text genre for this book')
    language = models.ForeignKey('Language', on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['title', 'author']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('book-detail', args=[str(self.id)])

    def display_genre(self):
        return ', '.join(genre.name for genre in self.genre.all()[:3])

    display_genre.short_description = 'Genre'


class BookInstance(models.Model):
    M = 'm'
    O = 'o'
    A = 'a'
    R = 'r'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          help_text='Unique Id for this particular book across the whole library')
    book = models.ForeignKey(Book, on_delete=models.RESTRICT, null=True)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)

    LOAN_STATUS = (
        (M, 'maintenance'),
        (O, 'On loan'),
        (A, 'Available'),
        (R, 'Reserved'),
    )

    status = models.CharField(max_length=1, choices=LOAN_STATUS, default='m', blank=True, help_text='Book Availability')
    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['due_back']
        permissions = (("can_mark_returned", "Set book as returned"),)

    def __str__(self):
        return f'{self.id} ({self.book.title})'

    @property
    def is_overdue(self):
        return bool(self.due_back and date.today() > self.due_back)


class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField('died', null=True, blank=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def get_absolute_url(self):
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self):
        return f'{self.last_name}, {self.first_name}'

class Language(models.Model):
    """Model representing a Language (e.g. English, French, Japanese, etc.)"""
    name = models.CharField(max_length=200,
                            help_text="Enter the book's natural language (e.g. English, French, Japanese etc.)")

    def __str__(self):
        """String for representing the Model object (in Admin site etc.)"""
        return self.name