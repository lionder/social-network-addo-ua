from rest_framework import serializers

from .models import Post
from users.models import User
from users.serializers import UserMiniSerializer


class PostDetailSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    users_liked = UserMiniSerializer(read_only=True, many=True)
    like_url = serializers.HyperlinkedIdentityField(view_name='post-like')
    unlike_url = serializers.HyperlinkedIdentityField(view_name='post-unlike')
    likes_count = serializers.ReadOnlyField()

    class Meta:
        model = Post
        fields = '__all__'
        read_only_fields = ('publication_time',)


class LikePostSerializer(PostDetailSerializer):
    current_user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault(),
        write_only=True
    )

    class Meta:
        model = Post
        fields = '__all__'
        read_only_fields = ('author', 'text', 'publication_time', 'users_liked')

    def update(self, instance, validated_data):
        instance.liked_by(validated_data['current_user'])
        instance.save()
        return instance

    def validate(self, data):
        if data['current_user'] == self.instance.author:
            raise serializers.ValidationError(
                'Author can not perform this action to his own post'
            )
        return data


class UnlikePostSerializer(LikePostSerializer):

    def update(self, instance, validated_data):
        instance.unliked_by(validated_data['current_user'])
        instance.save()
        return instance
