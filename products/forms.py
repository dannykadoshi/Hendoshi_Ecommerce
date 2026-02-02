from django import forms
from django.forms import inlineformset_factory, modelformset_factory
from .models import Product, ProductVariant, ProductImage, DesignStory, Collection
from .models import ProductType, ProductReview


class ProductForm(forms.ModelForm):
    """
    Main product creation/editing form
    """
    class Meta:
        model = Product
        fields = [
            'name',
            'description',
            'audience',
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
            'audience': forms.Select(attrs={
                'class': 'form-control auth-form-input',
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

    def clean_main_image(self):
        image = self.cleaned_data.get('main_image')
        if image:
            # Check if it's an image
            if not image.content_type in ['image/jpeg', 'image/png', 'image/webp']:
                raise forms.ValidationError('Please upload a valid image file (JPEG, PNG, or WebP).')
        return image

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
    Form for creating product variants (size/color combinations).
    Size and color are optional - they depend on the ProductType settings.
    """
    class Meta:
        model = ProductVariant
        fields = ['size', 'color', 'stock']
        widgets = {
            'size': forms.Select(attrs={
                'class': 'form-control auth-form-input',
            }),
            'color': forms.Select(attrs={
                'class': 'form-control auth-form-input',
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'form-control auth-form-input',
                'placeholder': 'Stock Quantity',
                'min': '0',
                'required': 'required'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make size and color not required by default - validation is based on ProductType
        self.fields['size'].required = False
        self.fields['color'].required = False

    def clean_stock(self):
        stock = self.cleaned_data.get('stock')
        if stock is None:
            raise forms.ValidationError('Stock quantity is required.')
        if stock < 0:
            raise forms.ValidationError('Stock quantity cannot be negative.')
        return stock


class VariantSelectionForm(forms.Form):
    """
    Form for selecting multiple sizes and colors at once to bulk-create variants.
    Uses checkboxes/toggles instead of individual variant forms.
    """
    # Size choices (excluding empty option)
    SIZE_CHOICES = [
        ('one_size', 'One Size'),
        ('xs', 'XS'),
        ('s', 'S'),
        ('m', 'M'),
        ('l', 'L'),
        ('xl', 'XL'),
        ('2xl', '2XL'),
        ('3xl', '3XL'),
        ('4xl', '4XL'),
        ('5xl', '5XL'),
    ]

    # Color choices (excluding empty option)
    COLOR_CHOICES = [
        ('n/a', 'N/A'),
        ('black', 'Black'),
        ('white', 'White'),
        ('charcoal', 'Charcoal Grey'),
        ('navy', 'Navy Blue'),
        ('red', 'Red'),
    ]

    sizes = forms.MultipleChoiceField(
        choices=SIZE_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'variant-toggle-checkbox',
        }),
        required=False,
        label='Available Sizes'
    )

    colors = forms.MultipleChoiceField(
        choices=COLOR_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'variant-toggle-checkbox',
        }),
        required=False,
        label='Available Colors'
    )

    default_stock = forms.IntegerField(
        min_value=0,
        initial=10,
        widget=forms.NumberInput(attrs={
            'class': 'form-control auth-form-input',
            'placeholder': 'Default stock for each variant',
            'min': '0',
        }),
        label='Default Stock per Variant',
        help_text='This stock value will be applied to all generated variants'
    )

    def get_selected_sizes(self):
        """Return list of selected size values"""
        return self.cleaned_data.get('sizes', [])

    def get_selected_colors(self):
        """Return list of selected color values"""
        return self.cleaned_data.get('colors', [])

    def generate_variants_data(self):
        """
        Generate variant combinations based on selected sizes and colors.
        Returns a list of dicts with size, color, and stock.
        """
        sizes = self.get_selected_sizes()
        colors = self.get_selected_colors()
        stock = self.cleaned_data.get('default_stock', 10)

        variants = []

        # If both sizes and colors are selected, create combinations
        if sizes and colors:
            for size in sizes:
                for color in colors:
                    variants.append({
                        'size': size,
                        'color': color,
                        'stock': stock
                    })
        # If only sizes are selected
        elif sizes:
            for size in sizes:
                variants.append({
                    'size': size,
                    'color': '',
                    'stock': stock
                })
        # If only colors are selected
        elif colors:
            for color in colors:
                variants.append({
                    'size': '',
                    'color': color,
                    'stock': stock
                })

        return variants


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
    Form for creating product design stories (optional)
    """
    class Meta:
        model = DesignStory
        fields = ['title', 'story', 'author', 'status']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control auth-form-input',
                'placeholder': 'Design Story Title (Optional)',
            }),
            'story': forms.Textarea(attrs={
                'class': 'form-control auth-form-input',
                'placeholder': 'Tell the story behind this design...',
                'rows': 8,
                'maxlength': '500',
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Default to 'published' so new design stories show immediately
        if not self.instance.pk:
            self.fields['status'].initial = 'published'
        # Make all fields optional
        for field in self.fields:
            self.fields[field].required = False

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get('title')
        story = cleaned_data.get('story')
        
        # If either title or story is provided, both should be provided
        if (title and not story) or (story and not title):
            raise forms.ValidationError('If you provide a design story, both title and content are required.')
        
        # If story is provided, check minimum length
        if story and len(story) < 20:
            raise forms.ValidationError('Story must be at least 20 characters long.')
        
        return cleaned_data
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
        fields = ['name', 'slug', 'category', 'requires_size', 'requires_color', 'requires_audience', 'default_stock']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control auth-form-input', 'required': True}),
            'slug': forms.TextInput(attrs={'class': 'form-control auth-form-input'}),
            'category': forms.Select(attrs={'class': 'form-control auth-form-input'}),
            'requires_size': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'requires_color': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'requires_audience': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'default_stock': forms.NumberInput(attrs={'class': 'form-control auth-form-input', 'min': '0'}),
        }
        help_texts = {
            'requires_size': 'If checked, customers must select a size when adding this product type to cart.',
            'requires_color': 'If checked, customers must select a color when adding this product type to cart.',
            'requires_audience': 'If checked, this product type requires audience selection (Men/Women/Kids/Unisex).',
            'default_stock': 'Default stock quantity for variants when creating products in bulk.',
        }


class ProductReviewForm(forms.ModelForm):
    """
    Form for submitting product reviews
    """
    class Meta:
        model = ProductReview
        fields = ['rating', 'title', 'review_text']
        widgets = {
            'rating': forms.RadioSelect(attrs={
                'class': 'star-rating-input',
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control auth-form-input',
                'placeholder': 'Give your review a title (optional)',
                'maxlength': '200',
            }),
            'review_text': forms.Textarea(attrs={
                'class': 'form-control auth-form-input',
                'placeholder': 'Share your experience with this product...',
                'rows': 5,
                'maxlength': '2000',
                'required': 'required',
            }),
        }
        labels = {
            'rating': 'Your Rating',
            'title': 'Review Title',
            'review_text': 'Your Review',
        }

    def clean_review_text(self):
        text = self.cleaned_data.get('review_text')
        if not text or len(text.strip()) < 20:
            raise forms.ValidationError('Review must be at least 20 characters.')
        return text.strip()

# ==================== BULK PRODUCT CREATION FORMS ====================

class BulkProductSelectionForm(forms.Form):
    """
    Step 1: Select multiple product types and audiences for bulk creation
    """
    product_types = forms.ModelMultipleChoiceField(
        queryset=ProductType.objects.all().order_by('category', 'name'),
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'product-type-checkbox',
        }),
        required=True,
        label='Select Product Types',
        help_text='Choose one or more product types to create'
    )
    
    audiences = forms.MultipleChoiceField(
        choices=[],  # Will be set in __init__
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'audience-checkbox',
        }),
        required=False,
        label='Select Audiences',
        help_text='Choose audiences (only applies to product types that require audience)'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set audience choices from Product model
        from .models import Product
        self.fields['audiences'].choices = Product.AUDIENCE_CHOICES
    
    def get_combinations(self):
        """
        Returns list of (product_type, audience) combinations.
        For product types that don't require audience, audience will be None.
        """
        product_types = self.cleaned_data.get('product_types', [])
        audiences = self.cleaned_data.get('audiences', [])
        
        combinations = []
        for pt in product_types:
            if pt.requires_audience and audiences:
                # Add combination for each audience
                for aud in audiences:
                    combinations.append((pt, aud))
            else:
                # Add single combination without audience
                combinations.append((pt, None))
        
        return combinations


class SharedBulkDataForm(forms.Form):
    """
    Shared data that applies to all products in the bulk creation
    """
    collection = forms.ModelChoiceField(
        queryset=Collection.objects.all().order_by('name'),
        widget=forms.Select(attrs={
            'class': 'form-control auth-form-input',
            'required': 'required'
        }),
        required=True,
        label='Collection (shared for all products)'
    )
    
    base_design_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control auth-form-input',
            'placeholder': 'e.g., "Skull Design", "Vintage Logo"',
            'required': 'required'
        }),
        required=True,
        label='Base Design Name',
        help_text='This will be used to generate product names'
    )
    
    base_description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control auth-form-input',
            'placeholder': 'Enter a template description. Use {{product_type}} and {{audience}} as placeholders.',
            'rows': 4,
            'required': 'required'
        }),
        required=True,
        label='Base Description Template',
        help_text='Use {{product_type}} and {{audience}} as placeholders'
    )
    
    meta_description = forms.CharField(
        max_length=160,
        widget=forms.Textarea(attrs={
            'class': 'form-control auth-form-input',
            'placeholder': 'SEO description template',
            'rows': 2,
            'maxlength': '160'
        }),
        required=False,
        label='Meta Description Template'
    )
    
    design_story_title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control auth-form-input',
            'placeholder': 'Design Story Title (optional)',
        }),
        required=False,
        label='Design Story Title (shared for all)'
    )
    
    design_story_content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control auth-form-input',
            'placeholder': 'Tell the story behind this design...',
            'rows': 4
        }),
        required=False,
        label='Design Story Content'
    )


class BulkProductItemForm(forms.Form):
    """
    Form for individual product item in bulk creation.
    Each product gets its own instance of this form.
    """
    # Hidden fields to track which combination this is
    product_type_id = forms.IntegerField(widget=forms.HiddenInput())
    audience = forms.CharField(widget=forms.HiddenInput(), required=False)
    
    # Product-specific fields
    name = forms.CharField(
        max_length=254,
        widget=forms.TextInput(attrs={
            'class': 'form-control auth-form-input bulk-product-name',
            'placeholder': 'Product Name',
            'required': 'required'
        }),
        required=True
    )
    
    base_price = forms.DecimalField(
        max_digits=6,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control auth-form-input bulk-product-price',
            'placeholder': 'Price (£)',
            'step': '0.01',
            'required': 'required'
        }),
        required=True
    )
    
    sale_price = forms.DecimalField(
        max_digits=6,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control auth-form-input',
            'placeholder': 'Sale Price (£) - Optional',
            'step': '0.01'
        }),
        required=False
    )
    
    main_image = forms.ImageField(
        widget=forms.FileInput(attrs={
            'class': 'form-control auth-form-input bulk-main-image',
            'accept': 'image/*',
            'required': 'required'
        }),
        required=True
    )
    
    # Note: Gallery images are handled separately in the view using request.FILES.getlist()
    # We won't define a form field for them here to avoid the multiple files widget issue
    
    # Variants
    sizes = forms.MultipleChoiceField(
        choices=[],  # Set in __init__
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'variant-size-checkbox',
        }),
        required=False
    )
    
    colors = forms.MultipleChoiceField(
        choices=[],  # Set in __init__
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'variant-color-checkbox',
        }),
        required=False
    )
    
    stock_per_variant = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control auth-form-input',
            'min': '0'
        }),
        required=False,
        label='Stock per Variant',
        help_text='Stock quantity for each size/color combination'
    )
    
    is_active = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        required=False,
        initial=True
    )
    
    featured = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        required=False,
        initial=False
    )
    
    def __init__(self, *args, product_type=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set size and color choices
        self.fields['sizes'].choices = ProductVariant.SIZE_CHOICES[1:]  # Exclude empty option
        self.fields['colors'].choices = ProductVariant.COLOR_CHOICES[1:]  # Exclude empty option
        
        # Set default stock from product type
        if product_type:
            self.fields['stock_per_variant'].initial = product_type.default_stock
            
            # If product type doesn't require size/color, hide those fields
            if not product_type.requires_size:
                self.fields['sizes'].widget = forms.HiddenInput()
            if not product_type.requires_color:
                self.fields['colors'].widget = forms.HiddenInput()
    
    def clean_main_image(self):
        image = self.cleaned_data.get('main_image')
        if image:
            if not image.content_type in ['image/jpeg', 'image/png', 'image/webp']:
                raise forms.ValidationError('Please upload a valid image file (JPEG, PNG, or WebP).')
        return image