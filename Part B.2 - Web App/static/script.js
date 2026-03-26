// Function to toggle the collapsible body
function toggleBody(id, link) {
  var elem = document.getElementById(id);
  if (elem.classList.contains('expanded')) {
    // Collapse the content
    elem.classList.remove('expanded');
    link.innerText = 'Read More';
  } else {
    // Expand to show full content
    elem.classList.add('expanded');
    link.innerText = 'Read Less';
  }
}

// On window load, check each collapsible body for overflow and hide the toggle link if not needed
window.addEventListener("load", function() {
  document.querySelectorAll('.collapsible-body').forEach(function(elem) {
    var toggleLink = document.querySelector('.toggle-link[data-target="' + elem.id + '"]');
    // If the content height (scrollHeight) is not greater than the container's height (clientHeight)
    // then hide the toggle link because there's no overflow.
    if (elem.scrollHeight <= elem.clientHeight) {
      if (toggleLink) {
        toggleLink.style.display = 'none';
      }
    }
  });
});


$(document).ready(function() {
            $(".nav-title").hover(
                function() {
                    $(".navbar").removeClass("bg-danger").addClass("bg-dark");
                },
                function() {
                    $(".navbar").removeClass("bg-dark").addClass("bg-danger");
                }
            );
        });