

echo $USER
echo $USER_ID
echo $GROUP_ID

sudo docker build \
    --network=host \
    --platform=linux/arm64 \
    -f Dockerfile \
    -t omni_directional_car_pi ..

