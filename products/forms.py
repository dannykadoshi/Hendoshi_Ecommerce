from django import forms
from django.forms import inlineformset_factory, modelformset_factory
from .models import Product, ProductVariant, ProductImage, DesignStory, Collection
from .models import ProductType


class ProductForm(forms.ModelForm):
    """
    Main product creation/editing form
    """
    class Meta:
        model = Product
        fields = [
            'name',
            'description',
            'collection',
            'product_type',
            'base_price',
            'sale_price',
            'sale_start',
            'sale_end',
            'main_image',
            'meta_description',
            'is_active',
            'featured'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control auth-form-input',
                'placeholder': 'Product Name',
                'required': 'required'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control auth-form-input',
                'placeholder': 'Product Description',
                'rows': 6,
                'required': 'required'
            }),
            'collection': forms.Select(attrs={
                'class': 'form-control auth-form-input',
                'required': 'required'
            }),
            'product_type': forms.Select(attrs={
                'class': 'form-control auth-form-input',
                'required': 'required'
            }),
            'base_price': forms.NumberInput(attrs={
                'class': 'form-control auth-form-input',
                'placeholder': 'Price (£)',
                'step': '0.01',
                'required': 'required'
            }),
            'sale_price': forms.NumberInput(attrs={
                'class': 'form-control auth-form-input',
                'placeholder': 'Sale Price (£) - Optional',
                'step': '0.01'
            }),
            'sale_start': forms.DateTimeInput(attrs={
                'class': 'form-control auth-form-input',
                'type': 'datetime-local',
                'placeholder': 'Sale Start Date/Time - Optional'
            }),
            'sale_end': forms.DateTimeInput(attrs={
                'class': 'form-control auth-form-input',
                'type': 'datetime-local',
                'placeholder': 'Sale End Date/Time - Optional'
            }),
            'main_image': forms.FileInput(attrs={
                'class': 'form-control auth-form-input',
                'accept': 'image/*',
                'required': 'required'
            }),
            'meta_description': forms.Textarea(attrs={
                'class': 'form-control auth-form-input',
                'placeholder': 'SEO Meta Description (max 160 chars)',
                'rows': 2,
                'maxlength': '160'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'featured': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise forms.ValidationError('Product name is required.')
        if len(name) < 3:
            raise forms.ValidationError('Product name must be at least 3 characters long.')
        return name

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if not description:
            raise forms.ValidationError('Product description is required.')
        if len(description) < 10:
            raise forms.ValidationError('Description must be at least 10 characters long.')
        return description

    def clean_base_price(self):
        price = self.cleaned_data.get('base_price')
        if not price:
            raise forms.ValidationError('Price is required.')
        if price <= 0:
            raise forms.ValidationError('Price must be greater than 0.')
        return price

    def clean_main_image(self):
        image = self.cleaned_data.get('main_image')
        # Only require image if creating new product (no instance yet)
        if not image and not self.instance.pk:
            raise forms.ValidationError('Main product image is required.')
        return image

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure collection select uses live DB queryset
        try:
            self.fields['collection'].queryset = Collection.objects.all().order_by('name')
        except Exception:
            pass

        # Use DB-backed ProductType choices when available
        try:
            self.fields['product_type'].queryset = ProductType.objects.all().order_by('name')
        except Exception:
            # If ProductType table isn't available (migration state), leave the field empty
            pass


class ProductVariantForm(forms.ModelForm):
    """
    Form for creating product variants (size/color combinations)
    """
    class Meta:
        model = ProductVariant
        fields = ['size', 'color', 'stock']
        widgets = {
            'size': forms.Select(attrs={
                'class': 'form-control auth-form-input',
                'required': 'required'
            }),
            'color': forms.Select(attrs={
                'class': 'form-control auth-form-input',
                'required': 'required'
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'form-control auth-form-input',
                'placeholder': 'Stock Quantity',
                'min': '0',
                'required': 'required'
            }),
        }

    def clean_stock(self):
        stock = self.cleaned_data.get('stock')
        if stock is None:
            raise forms.ValidationError('Stock quantity is required.')
        if stock < 0:
            raise forms.ValidationError('Stock quantity cannot be negative.')
        return stock


class ProductImageForm(forms.ModelForm):
    """
    Form for uploading additional product images
    """
    class Meta:
        model = ProductImage
        fields = ['image', 'alt_text', 'order']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control auth-form-input',
                'accept': 'image/*',
            }),
            'alt_text': forms.TextInput(attrs={
                'class': 'form-control auth-form-input',
                'placeholder': 'Alt text for image',
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control auth-form-input',
                'placeholder': 'Display order',
                'min': '0',
                'value': '0'
            }),
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        # Only require image if creating new image (no instance yet)
        if not image and not self.instance.pk:
            raise forms.ValidationError('Image is required.')
        return image


class DesignStoryForm(forms.ModelForm):
    """
    Form for creating product design stories
    """
    class Meta:
        model = DesignStory
        fields = ['title', 'story', 'author', 'status']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control auth-form-input',
                'placeholder': 'Design Story Title',
                'required': 'required'
            }),
            'story': forms.Textarea(attrs={
                'class': 'form-control auth-form-input',
                'placeholder': 'Tell the story behind this design...',
                'rows': 8,
                'maxlength': '500',
                'required': 'required',
                'oninput': 'updateCharCount(this)'
            }),
            'author': forms.TextInput(attrs={
                'class': 'form-control auth-form-input',
                'placeholder': 'Author Name',
                'value': 'HENDOSHI Design Team'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control auth-form-input',
            }),
        }

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if not title:
            raise forms.ValidationError('Design story title is required.')
        return title

    def clean_story(self):
        story = self.cleaned_data.get('story')
        if not story:
            raise forms.ValidationError('Design story is required.')
        if len(story) < 20:
            raise forms.ValidationError('Story must be at least 20 characters long.')
        if len(story) > 500:
            raise forms.ValidationError('Story must be at most 500 characters.')
        return story


# FormSets for managing multiple items
ProductVariantFormSet = inlineformset_factory(
    Product,
    ProductVariant,
    form=ProductVariantForm,
    extra=1,  # Show one empty form by default for create view
    can_delete=True
)

ProductImageFormSet = inlineformset_factory(
    Product,
    ProductImage,
    form=ProductImageForm,
    extra=1,  # Show one empty form by default for create view
    can_delete=True
)


class CollectionForm(forms.ModelForm):
    class Meta:
        model = Collection
        fields = ['name', 'slug', 'description', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control auth-form-input'}),
            'slug': forms.TextInput(attrs={'class': 'form-control auth-form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-control auth-form-input', 'rows': 3}),
        }


class ProductTypeForm(forms.ModelForm):
    class Meta:
        model = ProductType
        fields = ['name', 'slug']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control auth-form-input', 'required': True}),
            'slug': forms.TextInput(attrs={'class': 'form-control auth-form-input'}),
        }
