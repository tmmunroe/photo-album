echo "Generating lambda layer..."
./gen-lambda-layer.sh

echo "Running 'cdk synth' for deployment stack"
cdk synth PhotoAlbumDeploymentStack > templates/deployment.yml

echo "Running 'cdk synth' for lambda quick deploy stack"
cdk synth PhotoAlbumDeploymentStack/DeploymentStage/PhotoAlbumLambaQuickDeployStack > templates/lambda-deployment.yml

echo "Running 'cdk synth' for front end deployment stack"
cdk synth PhotoAlbumDeploymentStack/DeploymentStage/PhotoAlbumFrontendDeploymentStack > templates/frontend-deployment.yml

echo "Running 'cdk synth' for backend stack"
cdk synth PhotoAlbumDeploymentStack/DeploymentStage/PhotoAlbumStack > templates/backend.yml

echo "Running 'cdk synth' for frontend stack"
cdk synth PhotoAlbumDeploymentStack/DeploymentStage/PhotoAlbumFrontendStack > templates/frontend.yml
