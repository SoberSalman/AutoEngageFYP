function redirectToUserDashboard() {
    window.location.href = '/user-dashboard';
}

let productCount = 1;
const maxProducts = 3;

document.getElementById('addProductBtn').addEventListener('click', function() {
    if (productCount < maxProducts) {
        productCount++;
        const productSection = document.getElementById('productsSection');
        const newProduct = document.createElement('div');
        newProduct.className = 'form-group product-entry';
        newProduct.innerHTML = `
            <label for="product${productCount}">Product/Service ${productCount}</label>
            <input type="text" class="form-control mb-2" id="product${productCount}" name="product${productCount}" placeholder="Name">
            <textarea class="form-control mb-2" id="description${productCount}" name="description${productCount}" placeholder="Description" rows="2"></textarea>
            <textarea class="form-control mb-2" id="feature${productCount}" name="feature${productCount}" placeholder="Feature" rows="2"></textarea>
            <button type="button" class="remove-product-button">-</button>
        `;
        productSection.appendChild(newProduct);

        newProduct.querySelector('.remove-product-button').addEventListener('click', function() {
            productSection.removeChild(newProduct);
            productCount--;
            renumberProducts();
        });
    } else {
        Swal.fire({
            icon: 'warning',
            title: 'Warning',
            text: `You can only add up to ${maxProducts} products.`,
            confirmButtonText: 'Okay',
        });
    }
});

document.querySelector('.remove-product-button').addEventListener('click', function() {
    const productSection = document.getElementById('productsSection');
    const productEntry = this.parentElement;
    productSection.removeChild(productEntry);
    productCount--;
    renumberProducts();
});

function renumberProducts() {
    const products = document.querySelectorAll('.product-entry');
    products.forEach((product, index) => {
        const productNumber = index + 1;
        product.querySelector('label').setAttribute('for', `product${productNumber}`);
        product.querySelector('label').innerText = `Product/Service ${productNumber}`;
        product.querySelector('input[type="text"]').setAttribute('id', `product${productNumber}`);
        product.querySelector('input[type="text"]').setAttribute('name', `product${productNumber}`);
        product.querySelectorAll('textarea')[0].setAttribute('id', `description${productNumber}`);
        product.querySelectorAll('textarea')[0].setAttribute('name', `description${productNumber}`);
        product.querySelectorAll('textarea')[1].setAttribute('id', `feature${productNumber}`);
        product.querySelectorAll('textarea')[1].setAttribute('name', `feature${productNumber}`);
    });
}

document.getElementById('organizationForm').addEventListener('submit', function(event) {
    event.preventDefault();

    const organization_name = document.getElementById('organization_name').value;
    const formData = new FormData(this);
    const products = [];

    const productsSection = document.querySelectorAll('.product-entry');
    productsSection.forEach((product, index) => {
        const productNumber = index + 1;
        const productName = document.getElementById(`product${productNumber}`).value;
        const productDescription = document.getElementById(`description${productNumber}`).value;
        const productFeature = document.getElementById(`feature${productNumber}`).value;

        if (productName.trim() !== "" || productDescription.trim() !== "" || productFeature.trim() !== "") {
            products.push({
                name: productName,
                description: productDescription,
                feature: productFeature
            });
        }
    });

    formData.append('products', JSON.stringify(products));

    fetch('/create-organization', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.response) {
                Swal.fire({
                    icon: 'success',
                    title: 'Success',
                    text: `The organization "${organization_name}" has been created successfully!`,
                    confirmButtonText: 'Proceed to Dashboard'
                }).then(() => {
                    window.location.href = '/user-dashboard';
                });
            } else if (data.error) {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: data.error,
                    confirmButtonText: 'Try Again',
                });
            }
        })
        .catch(error => {
            Swal.fire({
                icon: 'error',
                title: 'Unexpected Error',
                text: 'Something went wrong. Please try again later.',
                confirmButtonText: 'Okay',
            });
            console.error('Error:', error);
        });
});
