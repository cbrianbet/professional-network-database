/*
 * Tests for the location/sub-location cascading dropdown in data-form.html
 * These tests can be run in a browser or adapted to a testing framework like Jest.
 */

// Mock the locationSubLocationMap from the original code
const locationSubLocationMap = {
    "Chemelil": ["Kimwani", "Chemelil"],
    "Tambul": ["Kamaina", "Tambul"],
    "Chemase": ["Kapkuong", "Kibigong"],
    "Kibisem": ["Kibisem", "Chemursoi"]
};

// Helper function to create a select element with given id and options
function createSelect(id, options) {
    const select = document.createElement('select');
    select.id = id;
    options.forEach(({value, text, selected, disabled}) => {
        const option = document.createElement('option');
        option.value = value;
        option.textContent = text;
        if (selected) option.selected = true;
        if (disabled) option.disabled = true;
        select.appendChild(option);
    });
    return select;
}

// Helper function to simulate the cascading dropdown logic
function setupCascadingDropdown() {
    // This is a simplified version of the logic from the template
    const locationSelect = document.getElementById('locationSelect');
    const subLocationSelect = document.getElementById('subLocationSelect');

    // We'll return an object with the elements and a function to trigger change
    return {
        locationSelect,
        subLocationSelect,
        triggerLocationChange: () => {
            const event = new Event('change');
            locationSelect.dispatchEvent(event);
        }
    };
}

// Test 1: Initial state - location enabled, sub-location disabled with correct placeholder
function testInitialState() {
    // Set up the DOM
    document.body.innerHTML = `
        <select id="locationSelect">
            <option value="">— Select location —</option>
            <option value="Chemelil">Chemelil</option>
            <option value="Tambul">Tambul</option>
        </select>
        <select id="subLocationSelect">
            <option value="" disabled selected>— Select sub-location —</option>
        </select>
    `;

    const locationSelect = document.getElementById('locationSelect');
    const subLocationSelect = document.getElementById('subLocationSelect');

    // Assertions
    assertFalse(locationSelect.disabled, 'Location select should be enabled initially');
    assertTrue(subLocationSelect.disabled, 'Sub-location select should be disabled initially');
    assertEquals(subLocationSelect.options[0].value, '', 'Sub-location should have empty value as first option');
    assertTrue(subLocationSelect.options[0].disabled, 'First sub-location option should be disabled');
    assertEquals(subLocationSelect.options[0].textContent, '— Select sub-location —', 'Sub-location placeholder text should be correct');

    return true;
}

// Test 2: Location change triggers sub-location population with correct options
function testLocationChangePopulatesSubLocation() {
    document.body.innerHTML = `
        <select id="locationSelect">
            <option value="">— Select location —</option>
            <option value="Chemelil">Chemelil</option>
            <option value="Tambul">Tambul</option>
        </select>
        <select id="subLocationSelect">
            <option value="" disabled selected>— Select sub-location —</option>
        </select>
    `;

    const locationSelect = document.getElementById('locationSelect');
    const subLocationSelect = document.getElementById('subLocationSelect');

    // Simulate selecting Chemelil
    locationSelect.value = 'Chemelil';
    locationSelect.dispatchEvent(new Event('change'));

    // Check that sub-location is enabled and has the correct options
    assertFalse(subLocationSelect.disabled, 'Sub-location should be enabled after location selection');
    assertEquals(subLocationSelect.options.length, 3, 'Should have 3 options (default + 2 sub-locations)');
    assertEquals(subLocationSelect.options[0].value, '', 'First option should be the default');
    assertTrue(subLocationSelect.options[0].disabled, 'First option should be disabled');
    assertEquals(subLocationSelect.options[1].value, 'Kimwani', 'Second option should be Kimwani');
    assertEquals(subLocationSelect.options[2].value, 'Chemelil', 'Third option should be Chemelil');

    // Now test with Tambul
    locationSelect.value = 'Tambul';
    locationSelect.dispatchEvent(new Event('change'));

    assertEquals(subLocationSelect.options.length, 3, 'Should have 3 options for Tambul');
    assertEquals(subLocationSelect.options[1].value, 'Kamaina', 'Second option should be Kamaina');
    assertEquals(subLocationSelect.options[2].value, 'Tambul', 'Third option should be Tambul');

    return true;
}

// Test 3: Selecting a location then a sub-location enables both fields for submission
// Note: In the actual code, both fields are always enabled for submission when not disabled.
// The sub-location field is disabled only when no location is selected.
// So this test checks that after selecting a location and a sub-location, both are enabled.
function testLocationAndSubLocationSelectionEnablesFields() {
    document.body.innerHTML = `
        <select id="locationSelect">
            <option value="">— Select location —</option>
            <option value="Chemelil">Chemelil</option>
        </select>
        <select id="subLocationSelect">
            <option value="" disabled selected>— Select sub-location —</option>
        </select>
    `;

    const locationSelect = document.getElementById('locationSelect');
    const subLocationSelect = document.getElementById('subLocationSelect');

    // Initially, location enabled, sub-location disabled
    assertFalse(locationSelect.disabled);
    assertTrue(subLocationSelect.disabled);

    // Select a location
    locationSelect.value = 'Chemelil';
    locationSelect.dispatchEvent(new Event('change'));

    // Now sub-location should be enabled
    assertFalse(subLocationSelect.disabled);

    // Select a sub-location
    subLocationSelect.value = 'Kimwani';
    // (no event needed for this test)

    // Both should be enabled (sub-location remains enabled after selection)
    assertFalse(locationSelect.disabled);
    assertFalse(subLocationSelect.disabled);

    return true;
}

// Test 4: Changing location resets sub-location options and selection
function testChangingLocationResetsSubLocation() {
    document.body.innerHTML = `
        <select id="locationSelect">
            <option value="">— Select location —</option>
            <option value="Chemelil">Chemelil</option>
            <option value="Tambul">Tambul</option>
        </select>
        <select id="subLocationSelect">
            <option value="" disabled selected>— Select sub-location —</option>
        </select>
    `;

    const locationSelect = document.getElementById('locationSelect');
    const subLocationSelect = document.getElementById('subLocationSelect');

    // Select Chemelil and then a sub-location
    locationSelect.value = 'Chemelil';
    locationSelect.dispatchEvent(new Event('change'));
    subLocationSelect.value = 'Kimwani';

    // Verify sub-location is set to Kimwani
    assertEquals(subLocationSelect.value, 'Kimwani');

    // Now change location to Tambul
    locationSelect.value = 'Tambul';
    locationSelect.dispatchEvent(new Event('change'));

    // Sub-location should reset to default (empty, disabled, selected)
    assertEquals(subLocationSelect.value, '');
    assertTrue(subLocationSelect.options[0].selected);
    assertTrue(subLocationSelect.options[0].disabled);
    // The options should now be for Tambul
    assertEquals(subLocationSelect.options.length, 3);
    assertEquals(subLocationSelect.options[1].value, 'Kamaina');
    assertEquals(subLocationSelect.options[2].value, 'Tambul');

    return true;
}

// Test 5: Form validation works correctly (required fields, disabled field handling)
// We'll test the validateField function from the template
function testFormValidation() {
    // We need to mock the validateField function because it's defined in the template
    // Let's extract the logic or mock the DOM for it.
    // The validateField function in the template:
    //   function validateField(input){
    //     const field=input.closest('.field');
    //     if(!field)return true;
    //     if(input.hasAttribute('disabled')) return true;
    //     let valid=true;
    //     if(input.required&&!input.value.trim())valid=false;
    //     if(input.type==='email'&&input.value&&!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(input.value))valid=false;
    //     if(input.type==='tel'&&input.value&&!/^[\d\s\+\-]{7,15}$/.test(input.value))valid=false;
    //     input.classList.toggle('invalid',!valid);
    //     field.classList.toggle('has-error',!valid);
    //     return valid;
    //   }
    //
    // We'll create a mock version for testing.

    // Set up a mock input and field container
    document.body.innerHTML = `
        <div class="field">
            <input id="testInput" type="text" required>
        </div>
    `;

    const testInput = document.getElementById('testInput');

    // Mock validateField function (copy from template)
    function validateField(input){
        const field=input.closest('.field');
        if(!field)return true;
        if(input.hasAttribute('disabled')) return true;
        let valid=true;
        if(input.required&&!input.value.trim())valid=false;
        // We'll skip email and tel for simplicity in this test
        input.classList.toggle('invalid',!valid);
        field.classList.toggle('has-error',!valid);
        return valid;
    }

    // Test with empty value (should be invalid)
    testInput.value = '';
    assertFalse(validateField(testInput), 'Empty required input should be invalid');
    assertTrue(testInput.classList.contains('invalid'), 'Input should have invalid class');
    assertTrue(testInput.parentElement.classList.contains('has-error'), 'Field should have has-error class');

    // Test with non-empty value (should be valid)
    testInput.value = 'Some value';
    assertTrue(validateField(testInput), 'Non-empty required input should be valid');
    assertFalse(testInput.classList.contains('invalid'), 'Input should not have invalid class');
    assertFalse(testInput.parentElement.classList.contains('has-error'), 'Field should not have has-error class');

    // Test disabled input (should be valid regardless)
    testInput.disabled = true;
    testInput.value = ''; // Even empty
    assertTrue(validateField(testInput), 'Disabled input should be considered valid');
    assertFalse(testInput.classList.contains('invalid'), 'Disabled input should not be invalid');

    return true;
}

// Test 6: Existing record loading properly sets both location and sub-location
// We'll test the logic in fillMemberForm that handles location and subLocation.
function testExistingRecordLoading() {
    // We'll mock the fillMemberForm logic for location and subLocation.
    // The relevant code:
    //   if (member.sub_location) {
    //     const subLocationValue = member.sub_location;
    //     let locationValue = '';
    //     for (const [loc, subs] of Object.entries(locationSubLocationMap)) {
    //       if (subs.includes(subLocationValue)) {
    //         locationValue = loc;
    //         break;
    //       }
    //     }
    //     const locationEl = document.querySelector('[name="location"]');
    //     if (locationEl) {
    //       locationEl.value = locationValue;
    //       locationEl.dispatchEvent(new Event('change'));
    //     }
    //     const subLocationEl = document.querySelector('[name="subLocation"]');
    //     if (subLocationEl) {
    //       subLocationEl.value = subLocationValue;
    //     }
    //   }
    //
    // We'll set up the DOM with the selects and then run this logic.

    document.body.innerHTML = `
        <select name="location" id="locationSelect">
            <option value="">— Select location —</option>
            <option value="Chemelil">Chemelil</option>
            <option value="Tambul">Tambul</option>
        </select>
        <select name="subLocation" id="subLocationSelect">
            <option value="" disabled selected>— Select sub-location —</option>
        </select>
    `;

    const locationSelect = document.getElementById('locationSelect');
    const subLocationSelect = document.getElementById('subLocationSelect');

    // Mock member with sub_location
    const member = { sub_location: 'Kimwani' };

    // Simulate the logic
    if (member.sub_location) {
        const subLocationValue = member.sub_location;
        let locationValue = '';
        for (const [loc, subs] of Object.entries(locationSubLocationMap)) {
            if (subs.includes(subLocationValue)) {
                locationValue = loc;
                break;
            }
        }
        const locationEl = document.querySelector('[name="location"]');
        if (locationEl) {
            locationEl.value = locationValue;
            locationEl.dispatchEvent(new Event('change'));
        }
        const subLocationEl = document.querySelector('[name="subLocation"]');
        if (subLocationEl) {
            subLocationEl.value = subLocationValue;
        }
    }

    // After processing, location should be set to Chemelil (since Kimwani is in Chemelil)
    assertEquals(locationSelect.value, 'Chemelil', 'Location should be set to Chemelil for sub-location Kimwani');
    // Sub-location should be set to Kimwani
    assertEquals(subLocationSelect.value, 'Kimwani', 'Sub-location should be set to Kimwani');
    // Sub-location select should be enabled (because location is set)
    assertFalse(subLocationSelect.disabled, 'Sub-location should be enabled after setting location');

    // Test another sub-location
    member.sub_location = 'Tambul';
    // Reset the selects
    locationSelect.value = '';
    subLocationSelect.value = '';
    subLocationSelect.innerHTML = '<option value="" disabled selected>— Select sub-location —</option>';

    // Re-run the logic
    if (member.sub_location) {
        const subLocationValue = member.sub_location;
        let locationValue = '';
        for (const [loc, subs] of Object.entries(locationSubLocationMap)) {
            if (subs.includes(subLocationValue)) {
                locationValue = loc;
                break;
            }
        }
        const locationEl = document.querySelector('[name="location"]');
        if (locationEl) {
            locationEl.value = locationValue;
            locationEl.dispatchEvent(new Event('change'));
        }
        const subLocationEl = document.querySelector('[name="subLocation"]');
        if (subLocationEl) {
            subLocationEl.value = subLocationValue;
        }
    }

    assertEquals(locationSelect.value, 'Tambul', 'Location should be set to Tambul for sub-location Tambul');
    assertEquals(subLocationSelect.value, 'Tambul', 'Sub-location should be set to Tambul');

    return true;
}

// Test 7: Edge cases like invalid locations, empty selections
function testEdgeCases() {
    document.body.innerHTML = `
        <select id="locationSelect">
            <option value="">— Select location —</option>
            <option value="Chemelil">Chemelil</option>
        </select>
        <select id="subLocationSelect">
            <option value="" disabled selected>— Select sub-location —</option>
        </select>
    `;

    const locationSelect = document.getElementById('locationSelect');
    const subLocationSelect = document.getElementById('subLocationSelect');

    // Test with empty location (should disable sub-location and reset to default)
    locationSelect.value = '';
    locationSelect.dispatchEvent(new Event('change'));

    assertTrue(subLocationSelect.disabled, 'Sub-location should be disabled when location is empty');
    assertEquals(subLocationSelect.options.length, 1, 'Sub-location should only have the default option');
    assertEquals(subLocationSelect.options[0].value, '');
    assertTrue(subLocationSelect.options[0].disabled);
    assertTrue(subLocationSelect.options[0].selected);

    // Test with a location not in the map (should still enable but with no sub-locations?)
    // Actually, the map has all locations from the template, but let's test a location not in the map.
    // We'll add an option not in the map.
    locationSelect.innerHTML += '<option value="Unknown">Unknown</option>';
    locationSelect.value = 'Unknown';
    locationSelect.dispatchEvent(new Event('change'));

    // For an unknown location, locationSubLocationMap[location] will be undefined, so subLocations will be []
    // The code: const subLocations = locationSubLocationMap[location] || [];
    // So it should be an empty array.
    // Then it will set the sub-location select to only have the default option and enable it.
    assertFalse(subLocationSelect.disabled, 'Sub-location should be enabled even for unknown location (but with no options)');
    // Actually, let's check the code again from the template:
    //   const subLocations = locationSubLocationMap[location] || [];
    //   subLocationSelect.innerHTML = '';
    //   // Add default disabled option
    //   const defaultOption = document.createElement('option');
    //   defaultOption.value = '';
    //   defaultOption.disabled = true;
    //   defaultOption.selected = true;
    //   defaultOption.textContent = '— Select sub-location —';
    //   subLocationSelect.appendChild(defaultOption);
    //   subLocations.forEach(subloc => {
    //     const option = document.createElement('option');
    //     option.value = subloc;
    //     option.textContent = subloc;
    //     subLocationSelect.appendChild(option);
    //   });
    //   // Enable sub-location select only if a location is selected
    //   subLocationSelect.disabled = !location;
    //
    // So for an unknown location, subLocations is empty array, so we only add the default option.
    // And since location is selected (non-empty), we enable the sub-location select.
    assertEquals(subLocationSelect.options.length, 1, 'Sub-location should only have the default option for unknown location');
    assertTrue(subLocationSelect.options[0].disabled);
    assertTrue(subLocationSelect.options[0].selected);
    assertEquals(subLocationSelect.options[0].textContent, '— Select sub-location —');

    return true;
}

// Helper assertion functions
function assertTrue(actual, message) {
    if (!actual) {
        throw new Error(`Assertion failed: ${message}`);
    }
}

function assertFalse(actual, message) {
    if (actual) {
        throw new Error(`Assertion failed: ${message}`);
    }
}

function assertEquals(expected, actual, message) {
    if (expected !== actual) {
        throw new Error(`Assertion failed: ${message}. Expected ${expected}, got ${actual}`);
    }
}

// Run all tests
function runTests() {
    const tests = [
        testInitialState,
        testLocationChangePopulatesSubLocation,
        testLocationAndSubLocationSelectionEnablesFields,
        testChangingLocationResetsSubLocation,
        testFormValidation,
        testExistingRecordLoading,
        testEdgeCases
    ];

    let passed = 0;
    let failed = 0;

    for (const test of tests) {
        try {
            // Reset DOM before each test
            document.body.innerHTML = '';
            const result = test();
            if (result !== false) {
                passed++;
                console.log(`✓ ${test.name}`);
            } else {
                failed++;
                console.log(`✗ ${test.name}: returned false`);
            }
        } catch (e) {
            failed++;
            console.log(`✗ ${test.name}: ${e.message}`);
        }
    }

    console.log(`\n${passed} passed, ${failed} failed`);
    return failed === 0;
}

// If this script is loaded in a browser, run the tests
if (typeof window !== 'undefined') {
    window.addEventListener('load', () => {
        const success = runTests();
        // Optionally, show result in the page
        const resultDiv = document.createElement('div');
        resultDiv.style.padding = '20px';
        resultDiv.style.fontFamily = 'monospace';
        resultDiv.innerHTML = `<h2>Test Results</h2><p>${success ? 'All tests passed' : 'Some tests failed'}</p>`;
        document.body.appendChild(resultDiv);
    });
}

// Export for use in other environments (like Node.js with jsdom)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        runTests,
        testInitialState,
        testLocationChangePopulatesSubLocation,
        testLocationAndSubLocationSelectionEnablesFields,
        testChangingLocationResetsSubLocation,
        testFormValidation,
        testExistingRecordLoading,
        testEdgeCases
    };
}