from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import Website, UserSession, SocialAccount

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        label='Passwort bestätigen'
    )
    website_id = serializers.UUIDField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'password2', 
                  'first_name', 'last_name', 'phone',
                  'street', 'street_number', 'city', 'postal_code', 'country',
                  'date_of_birth', 'company', 'website_id')
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
            'phone': {'required': False},
            'street': {'required': False},
            'street_number': {'required': False},
            'city': {'required': False},
            'postal_code': {'required': False},
            'country': {'required': False},
            'date_of_birth': {'required': False},
            'company': {'required': False},
        }
    
    def validate(self, attrs):
        """Validate that passwords match and check required fields for website."""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({
                "password": "Passwörter stimmen nicht überein."
            })
        
        # Check website-specific required fields
        website_id = attrs.pop('website_id', None)
        if website_id:
            try:
                website = Website.objects.get(id=website_id)
                
                # Validate required fields based on website settings
                if website.require_first_name and not attrs.get('first_name'):
                    raise serializers.ValidationError({'first_name': 'Dieses Feld ist erforderlich.'})
                if website.require_last_name and not attrs.get('last_name'):
                    raise serializers.ValidationError({'last_name': 'Dieses Feld ist erforderlich.'})
                if website.require_phone and not attrs.get('phone'):
                    raise serializers.ValidationError({'phone': 'Dieses Feld ist erforderlich.'})
                if website.require_address and not (attrs.get('street') and attrs.get('city') and attrs.get('postal_code')):
                    raise serializers.ValidationError({'address': 'Vollständige Adresse ist erforderlich.'})
                if website.require_date_of_birth and not attrs.get('date_of_birth'):
                    raise serializers.ValidationError({'date_of_birth': 'Dieses Feld ist erforderlich.'})
                if website.require_company and not attrs.get('company'):
                    raise serializers.ValidationError({'company': 'Dieses Feld ist erforderlich.'})
                    
                attrs['_website'] = website
            except Website.DoesNotExist:
                pass
        
        return attrs
    
    def create(self, validated_data):
        """Create a new user."""
        validated_data.pop('password2')
        website = validated_data.pop('_website', None)
        
        user = User.objects.create_user(**validated_data)
        
        # Grant access to website if specified
        if website:
            user.allowed_websites.add(website)
            # Check if profile is complete based on website requirements
            user.profile_completed = self._check_profile_completion(user, website)
            user.save()
        
        return user
    
    def _check_profile_completion(self, user, website):
        """Check if user profile is complete based on website requirements."""
        if website.require_first_name and not user.first_name:
            return False
        if website.require_last_name and not user.last_name:
            return False
        if website.require_phone and not user.phone:
            return False
        if website.require_address and not (user.street and user.city and user.postal_code):
            return False
        if website.require_date_of_birth and not user.date_of_birth:
            return False
        if website.require_company and not user.company:
            return False
        return True


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user details."""
    
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 
                  'phone', 'full_name', 'street', 'street_number', 'city', 
                  'postal_code', 'country', 'date_of_birth', 'company',
                  'profile_completed', 'is_active', 'is_verified', 
                  'date_joined', 'last_login',
                  'lexware_contact_id', 'lexware_customer_number')
        read_only_fields = ('id', 'email', 'date_joined', 'last_login', 'is_verified',
                          'lexware_contact_id', 'lexware_customer_number')


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile."""
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone', 'username',
                  'street', 'street_number', 'city', 'postal_code', 'country',
                  'date_of_birth', 'company')


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change.
    
    Requires the user's current password and the new password (twice for confirmation).
    """
    
    old_password = serializers.CharField(
        required=True, 
        style={'input_type': 'password'},
        help_text='Aktuelles Passwort des Benutzers',
        label='Altes Passwort'
    )
    new_password = serializers.CharField(
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'},
        help_text='Neues Passwort (mindestens 8 Zeichen)',
        label='Neues Passwort'
    )
    new_password2 = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        help_text='Neues Passwort (Bestätigung)',
        label='Neues Passwort (Wiederholung)'
    )
    
    def validate(self, attrs):
        """Validate that new passwords match."""
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({
                "new_password": "Neue Passwörter stimmen nicht überein."
            })
        return attrs


class WebsiteSerializer(serializers.ModelSerializer):
    """Serializer for website details."""
    
    class Meta:
        model = Website
        fields = ('id', 'name', 'domain', 'callback_url', 'is_active', 
                  'auto_register_users', 'created_at')
        read_only_fields = ('id', 'created_at')


class WebsiteCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new website."""
    
    class Meta:
        model = Website
        fields = ('name', 'domain', 'callback_url', 'auto_register_users')
    
    def create(self, validated_data):
        """Create a new website with auto-generated credentials."""
        import secrets
        validated_data['client_id'] = secrets.token_urlsafe(32)
        validated_data['client_secret'] = secrets.token_urlsafe(64)
        return super().create(validated_data)


class UserSessionSerializer(serializers.ModelSerializer):
    """Serializer for user sessions."""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    website_name = serializers.CharField(source='website.name', read_only=True)
    
    class Meta:
        model = UserSession
        fields = ('id', 'user_email', 'website_name', 'ip_address', 
                  'created_at', 'last_activity', 'expires_at', 'is_active')
        read_only_fields = fields


class SocialAccountSerializer(serializers.ModelSerializer):
    """Serializer for social accounts."""
    
    provider_display = serializers.CharField(source='get_provider_display', read_only=True)
    
    class Meta:
        model = SocialAccount
        fields = ('id', 'provider', 'provider_display', 'provider_user_id',
                  'email', 'first_name', 'last_name', 'avatar_url', 'created_at')
        read_only_fields = fields


class WebsiteRequiredFieldsSerializer(serializers.ModelSerializer):
    """Serializer for website required fields configuration."""
    
    class Meta:
        model = Website
        fields = ('id', 'name', 'domain',
                  'require_first_name', 'require_last_name', 'require_phone',
                  'require_address', 'require_date_of_birth', 'require_company')
        read_only_fields = ('id', 'name', 'domain')


class CompleteProfileSerializer(serializers.ModelSerializer):
    """Serializer for completing incomplete profiles."""
    
    website_id = serializers.UUIDField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone',
                  'street', 'street_number', 'city', 'postal_code', 'country',
                  'date_of_birth', 'company', 'website_id')
    
    def validate(self, attrs):
        """Validate required fields based on website configuration."""
        website_id = attrs.pop('website_id')
        
        try:
            website = Website.objects.get(id=website_id)
            
            if website.require_first_name and not attrs.get('first_name'):
                raise serializers.ValidationError({'first_name': 'Dieses Feld ist erforderlich.'})
            if website.require_last_name and not attrs.get('last_name'):
                raise serializers.ValidationError({'last_name': 'Dieses Feld ist erforderlich.'})
            if website.require_phone and not attrs.get('phone'):
                raise serializers.ValidationError({'phone': 'Dieses Feld ist erforderlich.'})
            if website.require_address:
                if not attrs.get('street'):
                    raise serializers.ValidationError({'street': 'Straße ist erforderlich.'})
                if not attrs.get('city'):
                    raise serializers.ValidationError({'city': 'Stadt ist erforderlich.'})
                if not attrs.get('postal_code'):
                    raise serializers.ValidationError({'postal_code': 'PLZ ist erforderlich.'})
            if website.require_date_of_birth and not attrs.get('date_of_birth'):
                raise serializers.ValidationError({'date_of_birth': 'Dieses Feld ist erforderlich.'})
            if website.require_company and not attrs.get('company'):
                raise serializers.ValidationError({'company': 'Dieses Feld ist erforderlich.'})
            
            attrs['_website'] = website
        except Website.DoesNotExist:
            raise serializers.ValidationError({'website_id': 'Website nicht gefunden.'})
        
        return attrs
    
    def update(self, instance, validated_data):
        """Update user profile and mark as completed."""
        website = validated_data.pop('_website')
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.profile_completed = True
        instance.save()
        
        # Grant access to website
        if not instance.allowed_websites.filter(id=website.id).exists():
            instance.allowed_websites.add(website)
        
        return instance
