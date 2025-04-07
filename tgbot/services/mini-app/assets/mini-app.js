const addOrderButton = document.getElementById('addOrderForm');
const orderFormsContainer = document.getElementById('orderFormsContainer');
const orderFormTemplate = document.getElementById('orderFormTemplate');

const productMaterialFDMTemplate = document.getElementById('productMaterialFDMTemplate');
const productMaterialSLATemplate = document.getElementById('productMaterialSLATemplate');

const sse = new EventSource(`/makeorder/events?user_id=${Telegram.WebApp.initDataUnsafe.user.id}`,
                            { withCredentials: true }); //Server-Side events connection with a bot

function setThemeClass() {
    document.documentElement.className = Telegram.WebApp.colorScheme;
}

async function post(adress, bodyDict) { //separate function for sending post requests
    //console.log(bodyDict)
    try {
        const response = await fetch(`/makeorder/${adress}`, {
            method: "POST",
            body: JSON.stringify(bodyDict)});

        if (!response.ok) {
            throw new Error(`Not OK: ${response.status}`);
        }

        const data = await response.text();
        //console.log(data)
        //window.body.innerHTML = `Answer: ${data}`;
    } catch (error) {
        console.log(`Something gone wrong: ${error.message}`);
        //window.body.innerHTML = `Error: ${error.message}`;
    }
};

async function modalManualClose() {
    await post("fileupload",
               { initData: `${Telegram.WebApp.initData}`,
               action: "cancel"})
}

async function elmentOrderId(element) { //finding an order id by given element
    const parentId = element.parentElement.parentElement.id;
    const start = parentId.indexOf("[");
    const end = parentId.indexOf("]");
    if (start !== -1 && end !== -1) {
        const order_id = parentId.slice(start + 1, end);
        return order_id
    }
}

async function orderTemplateElementPreparation(template, element_id) { //just a repetitive task for new order item elements
    element = template.querySelector(`#${element_id}`);
    element.id = `${element_id}[${orderCounter}]`;
    element.name = `${element_id}[${orderCounter}]`;
}

sse.onmessage = (event) => { //processing events from the telegram bot
    data = JSON.parse(event.data);
    productModel = document.getElementById(data.element_id)
    productModel.innerHTML = data.file_name
    modelId = data.element_id.replace("productModel", "productModelValue")
    productModelValue = document.getElementById(modelId)
    productModelValue.value = data.file_id
    const stlModal = bootstrap.Modal.getInstance(document.getElementById('stlModal'));
    stlModal.hide();
};

sse.onopen = () => {
    console.log("SSE opened");
};

sse.onerror = (error) => {
    console.error("SSE error:", error);
};

Telegram.WebApp.onEvent('themeChanged', setThemeClass);
setThemeClass();

orderFormsContainer.addEventListener('click', async (event) => { //event delegation
    console.log(event.target.id);
    if (event.target.id.startsWith('productModel')) { //setting the product model via telegram
        Telegram.WebApp.showConfirm("Будь ласка, завантажте STL-файл потрібний для цієї частини замовлення. Ви зможете змінити його до завершення завомлення.", async (is_ok) => {
            if(is_ok) {
                window.Telegram.WebApp.openTelegramLink("https://t.me/MetaPrint_assistant_bot");
                const stlModal = new bootstrap.Modal(document.getElementById('stlModal')); //hiding interface behind a modal untill either file is sent of modal is closed
                stlModal.show();
                await post("fileupload",
                     { initData: `${Telegram.WebApp.initData}`,
                       action: "sendFile",
                       element_id: `${event.target.id}`})
            }
        })
    }
    else if (event.target.id.startsWith('productTechnology')) { //choice of product technology
        productTechnology = event.target
        const selectedValue = productTechnology.value;
        order_id = await elmentOrderId(productTechnology)
        productTechnologyBonusContainer = document.getElementById(`productTechnologyBonusContainer[${order_id}]`);
        productTechnologyBonusContainer.innerHTML = ''
        const template = document.getElementById(`TechnologyTemplate-${selectedValue}`);
        if (template) {
            const clone = template.content.cloneNode(true);
            productTechnologyBonusContainer.appendChild(clone);
        }

        switch(selectedValue) {
            case "none":
                break;
            case "FDM":
                productMaterialFDM = templateDiv.querySelector('#productMaterialFDM');
                productMaterialFDM.id = `productMaterialFDM[${order_id}]`; ///
                productMaterialFDM.name = `productMaterial[${order_id}]`;
                productColorFDM = templateDiv.querySelector('#productColorFDM');
                productColorFDM.id = `productColorFDM[${order_id}]`;
                productColorFDM.name = `productColor[${order_id}]`;
                break;
            case "SLA":
                productMaterialSLA = templateDiv.querySelector('#productMaterialSLA');
                productMaterialSLA.id = `productMaterialSLA[${order_id}]`;
                productMaterialSLA.name = `productMaterial[${order_id}]`;
                break;
        }
    }
});

let orderCounter = 1;
addOrderButton.addEventListener('click', async (event) => { //Creating new order item
    const newOrderForm = orderFormTemplate.content.cloneNode(true);
    templateHeading = newOrderForm.querySelector('#headingOrderFormTemplate');
    templateHeading.id = `headingOrderForm[${orderCounter}`;
    templateButton = templateHeading.querySelector('.accordion-button');
    //console.log(templateButton.getAttribute('data-bs-target')); /////////////////////////////////////
    templateButton.setAttribute('data-bs-target', `#collapseOrderForm[${orderCounter}]`);
    templateButton.setAttribute('aria-controls', `collapseOrderForm[${orderCounter}]`);
    templateButton.innerHTML = `Замовлення #${orderCounter}`
    templateDiv = newOrderForm.querySelector('#collapseOrderFormTemplate');
    templateDiv.id = `collapseOrderForm[${orderCounter}]`;
    templateDiv.setAttribute('aria-labelledby', `headingOrderForm[${orderCounter}]`);
    /*templateProductModel = templateDiv.querySelector('.productModel');
    templateProductModel.id = `productModel${orderCounter}`;
    templateProductModel.addEventListener('click', (event) => {
        Telegram.WebApp.showPopup([{"title":"завантаження файлу", "message":"Будь ласка, завантажте STL-файл потрібний для цієї частини замовлення. Ви зможете змінити його до завершення завомлення."}])
        //Telegram.WebApp.sendData()
    });*/


    await orderTemplateElementPreparation(templateDiv, "productName")
    await orderTemplateElementPreparation(templateDiv, "productQuantity")
    await orderTemplateElementPreparation(templateDiv, "productModel")
    await orderTemplateElementPreparation(templateDiv, "productModelValue")
    await orderTemplateElementPreparation(templateDiv, "productTechnology")
    await orderTemplateElementPreparation(templateDiv, "productTechnologyBonusContainer")
    await orderTemplateElementPreparation(templateDiv, "productPostprocessing")

    orderFormsContainer.appendChild(newOrderForm);
    const addedForm = orderFormsContainer.lastElementChild;

    formButton = addedForm.querySelector('.accordion-button');
    formButton.click(); //set container as a current open one

    orderCounter++;
});


const mainForm = document.getElementById('mainForm');
mainForm.addEventListener('submit', async (event) => { //Custom form submission. Not complete. Need to add separate modal of confirmation.
    event.preventDefault();


    const formData = new FormData(mainForm);
    formData.append("initData", `${Telegram.WebApp.initData}`);
    fetch('/makeorder/submit-form', {
        method: 'POST',
        body: formData
    })
    .then(data => {
        console.log('Успех:', data);
    })
    .catch(error => {
        console.error('Ошибка:', error);
    });

    // Data in console
   /* for (const [name, value] of formData.entries()) {
        console.log(`${name}: ${value}`);
    }

    // Data in object
    const formObject = Object.fromEntries(formData.entries());
    console.log(formObject);*/
});



