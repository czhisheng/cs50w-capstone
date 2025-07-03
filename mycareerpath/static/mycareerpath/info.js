document.addEventListener('DOMContentLoaded', () => {
    document.addEventListener('click', event => {
        element = event.target;
        if (element.classList.contains('apply')) {
            if (document.querySelector(`#${element.dataset.a_id}`).dataset.applied) {
                event.preventDefault();
            }
            apply(element);
        }
    })
})

function display_info(element) {
    document.querySelector('.info').innerHTML = get_details(element);
}

function get_details(listing) {
    let logo = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/2048px-No_image_available.svg.png"
    
    if (listing.dataset.logo !== "") {
        logo = listing.dataset.logo
    }
    return (
        '<div class="info-top">' +
            `<div class="sect">
                <button onclick="like(this)" data-a_id="${ listing.id }" 
                  data-id="${ listing.dataset.id }" 
                  class="like btn ${ listing.dataset.saved
                    ?"btn-outline-danger" 
                    :"btn-outline-primary"}">
                    <i class="${ listing.dataset.saved?"bi-heart-fill":"bi-heart"}"></i>
                </button>
            </div>` +
            '<div class="sect-c"></div>' + 
            `<div class="sect">
                <a href="${ listing.dataset.job_link }" 
                   data-a_id="${ listing.id }" 
                   data-id="${ listing.dataset.id }" 
                   class="btn ${ listing.dataset.applied? "btn-outline-success" :"btn-outline-primary"} apply">
                      ${ listing.dataset.applied? "Applied": "Apply"}
                   </a>
            </div>` +
        '</div>' +
        '<div class="info-content">' +
            '<div>' +
                '<div class="info-title">' +
                    `<img class="listing-img p-2" src="${ logo }">` +
                    `<div class="company">${ listing.dataset.company }</div>` +
                    `<div class="mb-3 country">${ listing.dataset.location } (${ listing.dataset.type })</div>` +
                    `<h3 class="mb-3">${ listing.dataset.title }</h3>` +
                '</div>' +
            '</div><hr>' +
            '<div class="info-about">' +
                '<div class="about">About this job:</div>' +
                `<p>${ listing.dataset.desc }</p>` +
            '</div>' +
        '</div>'
    )
}


function like(element) {
    const id = element.dataset.id;
    element.disabled = true
    fetch('/save', {
        method: 'POST',
        headers: {'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value},
        body: JSON.stringify({
            id: id
        })
    })
    .then(response => response.json())
    .then(result => {
        if (result.saved) {
            document.querySelector(`#${element.dataset.a_id}`).dataset.saved = true;
            element.classList.remove("btn-outline-primary")
            element.classList.add("btn-outline-danger")
            element.querySelector('i').classList.remove("bi-heart")
            element.querySelector('i').classList.add("bi-heart-fill")
        }
        else {
            document.querySelector(`#${element.dataset.a_id}`).dataset.saved = "";
            element.classList.remove("btn-outline-danger")
            element.classList.add("btn-outline-primary")
            element.querySelector('i').classList.add("bi-heart")
            element.querySelector('i').classList.remove("bi-heart-fill")
        }
        element.disabled = false
    })
}


function apply(element) {
    const id = element.dataset.id;
    element.disabled = true
    fetch('/apply', {
        method: 'POST',
        headers: {'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value},
        body: JSON.stringify({
            id: id
        })
    })
    .then(response => response.json())
    .then(result => {
        if (result.applied) {
            document.querySelector(`#${element.dataset.a_id}`).dataset.applied = true;
            element.classList.remove("btn-outline-primary")
            element.classList.add("btn-outline-success")
            element.innerHTML = "Applied"
        }
        else {
            document.querySelector(`#${element.dataset.a_id}`).dataset.applied = "";
            element.classList.add("btn-outline-primary")
            element.classList.remove("btn-outline-success")
            element.innerHTML = "Apply"
        }
        element.disabled = false
    })
}