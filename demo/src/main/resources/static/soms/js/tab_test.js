// 관심지점 데이터 정의
let interestPoints = [
    {name: "관심지점1", coordinates: [35.458025, 129.327251], colorClass: "color1"},
    {name: "관심지점2", coordinates: [35.459039, 129.330517], colorClass: "color2"},
    {name: "관심지점3", coordinates: [35.461698, 129.334093], colorClass: "color3"},
    {name: "(주)태성환경연구소", coordinates: [35.456574, 129.327390], colorClass: "color4"}
];

const baseUrl = 'http://localhost:5000'; // 172.17.101.225:5001 /** flask와 맞춰주세요 */

let	defalut_lat = 35.456759;
let defalut_lot = 129.327684;

let infoWindow;
let selectedCheckbox = null; // 전역 변수로 선언
let selectedCoordinates = null;
let grid_lat = [];
let grid_lot = [];
let currentMarker = null; // 현재 마커를 저장하는 변수
let exist_id = 0;
let t_n = 0;
let id_t_n = [];
let modelingNum = 0;
let modelingSec = 0.0;
let normalDist = 0;

let rectangles = [];
let polylines = [];
let circles = []; 
let circles2 = [];
let runnings = [];

let predict_polylines = [];
let grid_space = 50;
let map;
let n_minute = 0; //;
let max11 = 11;

let first_grid_num;
let first_normal_num;
let first_date;
let first_t_n;
let first_id;
let visitedValues;
let predict_t_n;
 
let d_index;
let d_grid_num;
let d_normal_num;
let d_date;
let predictLineList = [];

let predictDateTime;
let predictCoordinates;
let markerPos;
let move_coor;

let no_m_name;
let no_center_lot;
let no_center_lat;
let no_wd;
let no_ws;
let none_location = true;
let customOverlays = [];

async function loadDataAndInitMap() {
    try {
        // 데이터 로드 비동기 작업 시작
        let response = await fetch(`${baseUrl}/setting_grid_code`, { method: 'POST' });
        let data = await response.json();

        // 데이터 처리 및 필요한 작업 수행
        // 예시: 데이터 처리 후 grid_lat과 grid_lot 변수에 값을 할당
        let list_check1 = [];
        let list_check2 = [];

        // 데이터를 객체로 변환하여 각 변수와 값을 모달 내에 표시
        for (const key in data) {
            if (data.hasOwnProperty(key)) {
                list_check1.push(key);
                list_check2.push(data[key]);
            }
        }

        grid_lat = list_check2[0];
        grid_lot = list_check2[1];

        // initMap()
        loadGoogleMapsAPI();
        //drawGrid();

    } catch (error) {
        console.error('Error:', error);
        // 에러 처리 로직
    }
}


document.addEventListener('DOMContentLoaded', function() {
    // API를 로드하는 함수를 호출합니다
	//loadGoogleMapsAPI();
    //initMap();
    loadDataAndInitMap();
    getWeather();
    //interest_point_table();
    date_time_search();
    checkbox_intetest_point();
    
    let navItems = document.querySelectorAll(".predict-nav-item");
    let tabContents = document.querySelectorAll(".predict-tab-item");

    // 탭의 초기 내용을 숨기는 함수
    function hideTabContents() {
        tabContents.forEach(content => content.style.display = "none");
    }

    // 첫 번째 탭 선택
    hideTabContents();
    tabContents[0].style.display = "block";
    
    navItems.forEach((item, index) => {
        item.addEventListener("click", function() {
            // 탭 내용을 숨기고
            hideTabContents();
            
            // 모든 탭에서 'predict-nav-item-on' 클래스 제거
            navItems.forEach(nav => nav.classList.remove("predict-nav-item-on"));

            // 클릭된 탭에 'predict-nav-item-on' 클래스 추가
            this.classList.add("predict-nav-item-on");

            // 클릭된 탭의 내용 보이기
            tabContents[index].style.display = "block";
        });
    });
	
    document.getElementById('mySlider').addEventListener('input', function(e) {
		
        let slider = e.target;
    
	    // Disable the slider
	    slider.disabled = true;
    	console.log("내가 선택한 슬라이더 값: ", slider.value);
    	
	    // 현재 슬라이더의 값 가져오기
	    let currentValue = parseInt(slider.value);
		
		//if (none_location == false){
	    // 처음에 왼쪽으로 슬라이드 시 한 칸씩만 ****
	    if(visitedValues.has(currentValue) || currentValue == slider.max) {
			visitedValues.add(currentValue);
			
			predict_t_n = 0;
			if(currentValue == max11){
				predict_t_n = max11;
			}
			else{
				predict_t_n = max11 - currentValue - 1;
			}
			usingSlider(predict_t_n);
			
		    slider.disabled = false;
		}
		else if(!visitedValues.has(currentValue)) {
			if (currentValue < parseInt(slider.max)){
				slider.disabled = false;
				let minValue = Math.min(...Array.from(visitedValues));
				slider.value = minValue - 1;
				currentValue = parseInt(slider.value);
				visitedValues.add(currentValue);
				
				predict_t_n = 0;
				if(currentValue == max11){
					predict_t_n = max11;
				}
				else{
					predict_t_n = max11 - currentValue - 1;
				}
				usingSlider(predict_t_n);
				
				console.log('현재 슬라이더 값', slider.value);
			}			
		}
	
		drawPredictLine(predict_t_n);
		//}
		
		if (none_location == true){
			//alert("바람길 예측 시 장소를 선택해주세요.");
		}
	});
});

// Google Maps API를 비동기적으로 로드합니다
function loadGoogleMapsAPI() {
    const script = document.createElement('script');
    script.src = `https://maps.googleapis.com/maps/api/js?key=AIzaSyCzxSPknsO4ZKNEf55FpCQl1Ukm0k7shQw&libraries=places,geometry&callback=initMapAndDrawGrid`;
    script.defer = true;
    document.head.appendChild(script);
}

function initMapAndDrawGrid() {
    initMap();
    interest_point_table();
    drawGrid();
}

// 구글맵 생성
function initMap() {
    // newMap div의 존재 여부를 확인
    var mapDiv = document.getElementById('newMap');
    if (!mapDiv) {
        console.error("newMap div가 존재하지 않습니다.");
        return;
    }
	
    var position = {
        lat: defalut_lat,
        lng: defalut_lot
    };
    var zoom = 16;
    var mapLocation = new google.maps.LatLng(position); // 지도에서 가운데로 위치할 위도와 경도
    var options = {
        center: mapLocation,
        zoom: zoom,
        mapId: "4504f8b37365c3d0",
        disableDefaultUI: true, //기본 UI 사용 여부
        disableDoubleClickZoom: true, //더블클릭 중심으로 확대 사용 여부
        draggable: true, //지도 드래그 이동 사용 여부
        keyboardShortcuts: false, //키보드 단축키 사용 여부
        maxZoom: 20, //최대 줌
        minZoom: 10, //최소 줌
        gestureHandling: 'greedy', //ctrl 없이 마우스 휠로 줌 가능
        zoomControl: false, // 지도의 확대/축소 수준을 변경하는 데 사용되는 "+"와 "-" 버튼을 표시합니다. 기본적으로 이 컨트롤은 지도의 오른쪽 아래 모서리에 나타납니다.
        mapTypeControl: true, // 드롭다운이나 가로 버튼 막대 스타일로 제공되며, 사용자가 지도 유형(ROADMAP, SATELLITE, HYBRID 또는 TERRAIN)을 선택할 수 있습니다. 이 컨트롤은 기본적으로 지도의 왼쪽 위 모서리에 나타납니다.
        mapTypeControlOptions: {
            style: google.maps.MapTypeControlStyle.HORIZONTAL_BAR,
            position: google.maps.ControlPosition.TOP_RIGHT
        },
        scaleControl: false, // 지도로 드래그해서 스트리트 뷰를 활성화할 수 있는 펙맨 아이콘이 있습니다. 기본적으로 이 컨트롤은 지도의 오른쪽 아래 근처에 나타납니다.
        streetViewControl: false, // 경사진 이미지가 포함된 지도에 틸트와 회전 옵션 조합을 제공합니다. 기본적으로 이 컨트롤은 지도의 오른쪽 아래 근처에 나타납니다. 자세한 내용은 45° 이미지를 참조하세요.
        rotateControl: true, // 지도 배율 요소를 표시합니다. 이 컨트롤은 기본적으로 비활성화되어 있습니다.
        mapTypeId: google.maps.MapTypeId.SATELLITE
        /* 기본 로드맵 보기를 표시합니다. */
    };
    
    map = new google.maps.Map(document.getElementById('newMap'), options);
    infoWindow = new google.maps.InfoWindow();
    
    //drawGrid();
    
    circleInterstPoints();

	// 지도 클릭 이벤트
	google.maps.event.addListener(map, 'click', function(event) {
	    if (currentMarker) {
	        currentMarker.setMap(null);
	    }
	    
	    // 클릭한 위치에 새로운 마커를 추가합니다.
	    currentMarker = new google.maps.Marker({
	        position: event.latLng,
	        map: map
	    });
	    
	    markerPos = event.latLng;
	    
	    // 모달 창을 엽니다.
	    openModal();
	});
}
	
function circleInterstPoints(){
	removeCircles();
	removeNames();
	
	function CustomOverlay(map, position, text) {
	    this.map = map;
	    this.position = position;
	    this.text = text;
	    this.div = null;
	    this.setMap(map);
	}
	
	CustomOverlay.prototype = new google.maps.OverlayView();
	
	CustomOverlay.prototype.onAdd = function() {
	    var div = document.createElement('div');
	    div.style.position = 'absolute';
	    div.style.fontSize = '12px';
	    div.appendChild(document.createTextNode(this.text));
	    this.div = div;
	    var panes = this.getPanes();
	    panes.overlayLayer.appendChild(div);
	};
	
	CustomOverlay.prototype.draw = function() {
	    var overlayProjection = this.getProjection();
	    var position = overlayProjection.fromLatLngToDivPixel(this.position);
	    var div = this.div;
	    div.style.left = position.x + 20 + 'px';
	    div.style.top = position.y - 10 + 'px';
	    div.style.color = 'white';
	    div.style.fontWeight = 'bold';
	    div.style.textShadow = '-1px 0 black, 0 1px black, 1px 0 black, 0 -1px black';
	    div.style.zIndex = 1001;
	};
	
	CustomOverlay.prototype.onRemove = function() {
	    this.div.parentNode.removeChild(this.div);
	    this.div = null;
	};
	
    interestPoints.forEach(point => {
		const actualColor = getColorFromClass(point.colorClass);
		
        const center = new google.maps.LatLng(point.coordinates[0], point.coordinates[1]);
        
	    const cityCircle = new google.maps.Circle({
	        strokeColor: '#FFFFFF',
	        strokeOpacity: 1.0,
	        strokeWeight: 2.5,
	        fillColor: actualColor,
	        fillOpacity: 1.0,
	        zIndex: 1000,
	        map: map,
	        center: center,
	        radius: 20  // 이 값은 원의 크기를 조절합니다. 필요에 따라 조정하십시오.
	    });
	    
        google.maps.event.addListener(cityCircle, 'click', function(event) {
			const lat = event.latLng.lat();
			const lng = event.latLng.lng();
			
			deleteCircle(lat, lng);
			
		    if (currentMarker){
				currentMarker.setMap(null);
				currentMarker = null;
			}
			
		    document.getElementById('deleteButton').onclick = function() {
		        // 여기에 관심지점 삭제 로직 추가
		        closeModal();
    
			    const circleCenter = cityCircle.getCenter();
			    console.log("circleCenter: ", circleCenter);
			
			    const indexToRemove = interestPoints.findIndex(p =>
			        p.coordinates[0] === circleCenter.lat() &&
			        p.coordinates[1] === circleCenter.lng());
			
			    if (indexToRemove !== -1) {
			        interestPoints.splice(indexToRemove, 1);
			        
		            const overlay = customOverlays.find(overlay => 
		                overlay.position.equals(circleCenter));
		            overlay.setMap(null);
		            customOverlays.splice(customOverlays.indexOf(overlay), 1);
			    }
				infoWindow.close();
				interest_point_table();
				checkbox_intetest_point();
				circleInterstPoints();
				
			    cityCircle.setMap(null);
			    //여기
			    clearSensorCircles(circles);
			    clearRunningSensors(runnings);
		    }
        });

        map.addListener('zoom_changed', function () {
		    const zoom = map.getZoom();
		    const radius = calculateRadius(zoom);
		    cityCircle.setRadius(radius);
		});
			
        circles2.push(cityCircle);
        
        // 텍스트 오버레이 생성 및 맵에 추가
        var customOverlay = new CustomOverlay(map, center, point.name);
        customOverlays.push(customOverlay);
    });
}

function fromLatLngToPixel(lat, lng) {
    var projection = map.getProjection();
    var bounds = map.getBounds();

    var sw = projection.fromLatLngToPoint(bounds.getSouthWest());
    var ne = projection.fromLatLngToPoint(bounds.getNorthEast());

    var scale = Math.pow(2, map.getZoom());
    var worldPoint = projection.fromLatLngToPoint(new google.maps.LatLng(lat, lng));
    
    return {x: (worldPoint.x - sw.x) * scale, y: (worldPoint.y - ne.y) * scale};
}

function deleteCircle(lat, lng){
	closeModal();
	
	var pixel = fromLatLngToPixel(lat, lng);
	
	// 모달 div 생성
	let modal = document.createElement('div');
	modal.id = 'modal-marker2';
	modal.style.display = 'block';
	modal.style.position = 'fixed';
	modal.style.top = (pixel.y + 25) + 'px';
	modal.style.left = (pixel.x - 70) + 'px';
	modal.style.backgroundColor = '#1A305F';
	modal.style.border = '3px solid #03153A';
	modal.style.borderRadius = '8px';
	modal.style.boxShadow = '0 3px 10px rgba(0, 0, 0, 0.2)';
	modal.style.color = 'white'; // 모달의 기본 텍스트 색상을 흰색으로 설정
	modal.style.width = '150px';
	modal.style.height = '50px';
	
	// 관심지점 삭제 버튼 추가
	let deleteButton = document.createElement('button');
	deleteButton.innerText = '해당 관심지점 삭제';
	deleteButton.style.position = 'absolute';
	deleteButton.style.top = '50%';
	deleteButton.style.left = '5px';
	deleteButton.style.transform = 'translate(0, -50%)';
	deleteButton.style.color = 'white';
	deleteButton.style.padding = '5px';
	deleteButton.style.marginRight = '10px';
	deleteButton.style.borderRadius = '5px';
	deleteButton.style.backgroundColor = '#0075ff';
	deleteButton.style.fontWeight = 'bold';
	deleteButton.style.fontSize = '12px';
	deleteButton.style.border = '2px solid #1A305F';
	deleteButton.id = 'deleteButton';
	
	modal.appendChild(deleteButton);
	
	// X 버튼 추가
	let closeButton = document.createElement('button');
	closeButton.innerText = 'X';
	closeButton.style.position = 'absolute';
	closeButton.style.top = '50%';
	closeButton.style.right = '7px';
	closeButton.style.transform = 'translate(0, -50%)';
	closeButton.style.background = 'transparent';
	closeButton.style.border = 'none';
	closeButton.style.cursor = 'pointer';
	closeButton.style.color = 'white';
	closeButton.onclick = function() {
	    closeModal();
	};
	
	modal.appendChild(closeButton);
	
	document.body.appendChild(modal);
}


function removeCircles() {
    circles2.forEach(circle2 => {
        circle2.setMap(null); // 각 원에서 지도를 제거
    });
    circles2 = []; // 배열을 초기화하여 참조를 제거
}

function removeNames() {
    customOverlays.forEach(customOverlay => {
        customOverlay.setMap(null); // 각 원에서 지도를 제거
    });
    customOverlays = []; // 배열을 초기화하여 참조를 제거
}

function openModal() {
    closeModal();

    // 모달 div 생성
    let modal = document.createElement('div');
    modal.id = 'modal-marker';
    modal.style.display = 'block';
    modal.style.position = 'fixed';
    modal.style.right = '350px';
    modal.style.bottom = '150px';
    modal.style.backgroundColor = '#1A305F';
    modal.style.padding = '20px';
    modal.style.border = '3px solid #03153A';
    modal.style.borderRadius = '8px';
    modal.style.boxShadow = '0 3px 10px rgba(0, 0, 0, 0.2)';
    modal.style.color = 'white'; // 모달의 기본 텍스트 색상을 흰색으로 설정

    // X 버튼 추가
    let closeButton = document.createElement('button');
    closeButton.innerText = 'X';
    closeButton.style.position = 'absolute';
    closeButton.style.right = '10px';
    closeButton.style.top = '10px';
    closeButton.style.background = 'transparent';
    closeButton.style.border = 'none';
    closeButton.style.cursor = 'pointer';
    closeButton.style.color = 'white';
    closeButton.onclick = function() {
	    if (currentMarker){
			currentMarker.setMap(null);
			currentMarker = null;
		}
		closeModal();
	}
    modal.appendChild(closeButton);

    // 테이블로 내부 요소 정렬
    let table = document.createElement('table');
    table.style.width = '100%';
    table.style.textAlign = 'center'; // 내부 요소 가운데 정렬
    
    // 제목 행 추가
    let titleRow = table.insertRow();
    let titleCell = titleRow.insertCell();
    titleCell.colSpan = 2; // 두 칸을 합치기
    titleCell.innerText = '관심지점 추가';
    titleCell.style.fontSize = '15px'; // 글씨 크기 조절
    titleCell.style.fontWeight = 'bold';
    titleCell.style.paddingBottom = '10px'; // 아래 여백 추가

    // 위도 및 경도 행 추가
	let latRow = table.insertRow();
	let latCell = latRow.insertCell();
	latCell.colSpan = 2;
	latCell.style.textAlign = 'center';
	latCell.style.paddingTop = '10px'; // 위쪽 여백 추가
	latCell.style.paddingBottom = '10px'; // 아래쪽 여백 추가
	let latLabel = document.createElement('span');
	latLabel.innerText = '위도:';
	latLabel.style.fontSize = '12px';
	latLabel.style.fontWeight = 'bold';
	latCell.appendChild(latLabel);
	let latInput = document.createElement('input');
	latInput.type = 'text';
	latInput.style.width = '50%';
	latInput.style.height = '20px';
	latInput.style.lineHeight = '20px';
	latInput.style.fontSize = '12px';
	latInput.style.marginLeft = '10px';
	latInput.style.textAlign = 'center';
	latInput.value = markerPos.lat().toFixed(5);
	latInput.onchange = function() {
	    let newLat = parseFloat(this.value);
	    if (!isNaN(newLat)) {
	        markerPos = new google.maps.LatLng(newLat, markerPos.lng());
	        currentMarker.setPosition(markerPos);
	    }
	};
	latCell.appendChild(latInput);

	let lngRow = table.insertRow();
	let lngCell = lngRow.insertCell();
	lngCell.colSpan = 2;
	lngCell.style.textAlign = 'center';
	latCell.style.paddingTop = '10px'; // 위쪽 여백 추가
	latCell.style.paddingBottom = '10px'; // 아래쪽 여백 추가
	let lngLabel = document.createElement('span');
	lngLabel.innerText = '경도:';
	lngLabel.style.fontSize = '12px';
	lngLabel.style.fontWeight = 'bold';
	lngCell.appendChild(lngLabel);
	let lngInput = document.createElement('input');
	lngInput.type = 'text';
	lngInput.style.width = '50%';
	lngInput.style.height = '20px';
	lngInput.style.fontSize = '12px';
	lngInput.style.lineHeight = '20px';
	lngInput.style.marginLeft = '10px';
	lngInput.style.textAlign = 'center';
	lngInput.value = markerPos.lng().toFixed(5);
	lngInput.onchange = function() {
	    let newLng = parseFloat(this.value);
	    if (!isNaN(newLng)) {
	        markerPos = new google.maps.LatLng(markerPos.lat(), newLng);
	        currentMarker.setPosition(markerPos);
	    }
	};
	lngCell.appendChild(lngInput);
    
    // textarea 행 추가
	let textareaRow = table.insertRow();
	let textareaCell = textareaRow.insertCell();
	textareaCell.colSpan = 2;
	textareaCell.style.paddingTop = '10px'; // 위쪽 여백 추가
	let textarea = document.createElement('textarea');
	textarea.placeholder = "새로운 관심지점명...";
	textarea.style.width = '75%';
	textarea.style.height = '30px';
	textarea.style.lineHeight = '30px';  // 이 부분 추가
	textarea.style.marginBottom = '10px'; // 행간 조절
	textarea.style.textAlign = 'center';
	textarea.style.fontSize = '12px';
	textareaCell.style.textAlign = 'center';
	textareaCell.appendChild(textarea);

    // 버튼 행 추가
    let buttonRow = table.insertRow();
    let confirmButtonCell = buttonRow.insertCell();
    confirmButtonCell.colSpan = 2; // 셀 병합
    confirmButtonCell.style.textAlign = 'center'; // 가운데 정렬

    // 확인 버튼 추가
    let confirmButton = document.createElement('button');
    confirmButton.innerText = '확인';
    confirmButton.style.width = '60px';
    confirmButton.style.backgroundColor = '#0075ff';
    confirmButton.style.color = 'white';
    confirmButton.style.fontWeight = 'bold';
    confirmButton.style.fontSize = '12px';
    confirmButton.style.borderRadius = '5px';
    confirmButton.style.border = '2px solid #1A305F';
	
    confirmButton.onclick = function() {
	    if (currentMarker){
			currentMarker.setMap(null);
			currentMarker = null;
		}
		closeModal();
		clearSensorCircles(circles);
		clearRunningSensors(runnings);
		
		//관심지점에 추가하기 markerPos.lat(), markerPos.lot()
		let minLat = Math.min(...grid_lat);
		let maxLat = Math.max(...grid_lat);
		let minLon = Math.min(...grid_lot);
		let maxLon = Math.max(...grid_lot);
		
		if (markerPos.lat() >= minLat && markerPos.lat() <= maxLat && markerPos.lng() >= minLon && markerPos.lng() <= maxLon) {
			if(textarea.value.trim() != ""){
				let newPointName = textarea.value;
				// 새로운 관심 지점을 정의합니다.
				// 마지막 요소의 colorClass 값을 가져옵니다.
				let lastColorClass = interestPoints[interestPoints.length - 1].colorClass;
				// 숫자 부분만 추출하고 정수로 변환합니다.
				let lastColorNumber = parseInt(lastColorClass.replace("color", ""));
				// 색상을 순환합니다. 예를 들어 10가지 색상만 있다고 가정합니다.
				let newColorNumber = (lastColorNumber % 10) + 1;
				let newColorClass = "color" + newColorNumber;
				
				// 새로운 관심 지점을 정의합니다.
				let newPoint = {
				    name: newPointName,
				    coordinates: [markerPos.lat(), markerPos.lng()],
				    colorClass: newColorClass
				};
				
				console.log("interestPoints: ", interestPoints);
				// interestPoints 배열에 새로운 관심 지점을 추가합니다.
				interestPoints.push(newPoint);	
				
				interest_point_table();
				checkbox_intetest_point();
				circleInterstPoints();
			}
			else {
				alert("새로운 관심지점명을 입력해주세요.");
			}
		}
		else {
			alert("관심지점은 그리드 내에 위치해야 합니다.");
		}
	}

    confirmButtonCell.appendChild(confirmButton);
    modal.appendChild(table);
    document.body.appendChild(modal);
}

function closeModal() {
	let modal2 = document.getElementById("modal-marker2");
	if (modal2){
		document.body.removeChild(modal2);
	}
    let modal = document.getElementById("modal-marker");
    if (modal) {
        document.body.removeChild(modal);
    }
}
	
function getColorFromClass(className) {
    const element = document.createElement('div');
    element.className = className;
    document.body.appendChild(element);
    const color = window.getComputedStyle(element).color;
    document.body.removeChild(element);
    return color;
}

function drawGrid(){
	let con1;
	console.log("grid_space: ", grid_space);
	function condition1(i){
		if (grid_space <= 50){
			con1 = ((i + 1) % 3 === 1);
		}
		else {
			con1 = true;
		}
		return con1;
	}
	// 나중에 3X3 격자 확대 수정 예정
	// 세로선 그리기
	for (let i = 0; i < grid_lot.length; i++) {
		if (condition1(i)) {
		    let verticalLine = [];
		    for (let j = 0; j < grid_lat.length; j++) {
		        verticalLine.push({ lat: grid_lat[j], lng: grid_lot[i] });
		    }
		    let polylineOptions = {
		        path: verticalLine,
		        strokeColor: 'red',
		        strokeOpacity: 1.0,
		        strokeWeight: 0.8,
		    };
		    let polyline = new google.maps.Polyline(polylineOptions);
		    polyline.setMap(map);
		}
	}
	
	// 가로선 그리기
	for (let i = 0; i < grid_lat.length; i++) {
		if (condition1(i)) {
		    let horizontalLine = [];
		    for (let j = 0; j < grid_lot.length; j++) {
		        horizontalLine.push({ lat: grid_lat[i], lng: grid_lot[j] });
		    }
		    let polylineOptions = {
		        path: horizontalLine,
		        strokeColor: 'red',
		        strokeOpacity: 0.5,
		        strokeWeight: 1.5,
		    };
		    let polyline = new google.maps.Polyline(polylineOptions);
		    polyline.setMap(map);
		}
	}
}

// 실시간으로 날짜와 시간을 업데이트하는 함수
function updateDateTime() {
    let today = new Date();
    let year = today.getFullYear();
    let month = today.getMonth() + 1;
    if (month < 10) {
        month = '0' + month;
    }
    let date = today.getDate();
    if (date < 10) {
        date = '0' + date;
    }
    let hours = today.getHours();
    if (hours < 10) {
        hours = '0' + hours;
    }
    let minutes = today.getMinutes();
    if (minutes < 10) {
        minutes = '0' + minutes;
    }
    let seconds = today.getSeconds();
    if (seconds < 10) {
        seconds = '0' + seconds;
    }

    $('#nowDate').text(year + "-" + month + "-" + date);
    $('#nowTime').text(hours + ":" + minutes + ":" + seconds);
}

// 매 초마다 updateDateTime 함수를 실행
setInterval(updateDateTime, 1000);

function getWeather() {
    let today = new Date();
    let year = today.getFullYear();
    let month = today.getMonth() + 1;
    if (month < 10) {
        month = '0' + month;
    }
    let date = today.getDate();
    if (date < 10) {
        date = '0' + date;
    }
    let hours = today.getHours() - 1;
    if (hours < 10) {
        hours = '0' + hours;
    }
    hours = hours + '30';

    var xhr = new XMLHttpRequest();
    var url = 'http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst'; /*URL*/
    var queryParams = '?' + encodeURIComponent('serviceKey') + '=' + 'hbRF1buCgCD2QmVbJsSlK%2FOM8C7k0TiQvm7RYKkHxtzki1cA%2F329DNNLNMqJiogP6mcqfpxEQTO5XuhVUYyujg%3D%3D'; /*Service Key*/
    queryParams += '&' + encodeURIComponent('pageNo') + '=' + encodeURIComponent('1');
    queryParams += '&' + encodeURIComponent('numOfRows') + '=' + encodeURIComponent('1000');
    queryParams += '&' + encodeURIComponent('dataType') + '=' + encodeURIComponent('JSON');
    queryParams += '&' + encodeURIComponent('base_date') + '=' + encodeURIComponent(year + month + date);
    queryParams += '&' + encodeURIComponent('base_time') + '=' + encodeURIComponent(hours);
    queryParams += '&' + encodeURIComponent('nx') + '=' + encodeURIComponent('102');
    queryParams += '&' + encodeURIComponent('ny') + '=' + encodeURIComponent('81');
    xhr.open('GET', url + queryParams);
    xhr.onreadystatechange = function() {
        if (this.readyState == 4) {
			//console.log(this.responseText);
			
            var obj = JSON.parse(this.responseText);
            obj = obj.response.body.items.item;

            var pty = obj[0].obsrValue;
            var humi = obj[1].obsrValue;
            var rain = obj[2].obsrValue;
            var temp = obj[3].obsrValue;
            var wdegree = obj[5].obsrValue;
            var wspeed = obj[7].obsrValue;
			
            $('#nowTemp').text(temp + '℃');
            $('#nowHumi').text(humi + '％');
            $('#nowSpeed').text(wspeed + '㎧');
            $('#nowDirection').text(transfer_WindKO(wdegree));
            $('#arrows').attr('class', 'arrow ' + transfer_WindENG(wdegree));
            $('#wind').attr('class', 'wind ' + transfer_WindENG(wdegree));
        }
    };
    xhr.send('');
}

function transfer_WindKO(deg) {
    var val = Math.floor((deg / 22.5) + .5);
    arr = ["북", "북북동", "북동", "동북동", "동", "동남동", "남동", "남남동", "남", "남남서", "남서", "서남서", "서", "서북서", "북서", "북북서"];
    return arr[(val) % 16];
}

function transfer_WindENG(deg) {
    var val = Math.floor((deg / 22.5) + .5);
    arr = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"];
    return arr[(val) % 16];
}
 
function interest_point_table(){
    const interestTable = document.getElementById("interest-point");
    interestTable.innerHTML = '';
	
	// interestPoints 부분을 위한 내부 테이블 생성
	const interestInnerTable = document.createElement("table");
	const interestTr = document.createElement("tr");
	const interestTd = document.createElement("td");

    interestPoints.forEach(point => {
        const tr1 = document.createElement("tr");

        const td1 = document.createElement("td");
        const circle = document.createElement("div");
        circle.className = `circle ${point.colorClass}`;
        td1.appendChild(circle);
		td1.style.padding = '5px';
		td1.style.paddingLeft = '10px';
		td1.style.paddingTop = '2px';
		
        const td11 = document.createElement("td");
        const link = document.createElement("a");
		link.href = "#";
		link.textContent = point.name;
		link.style.color = "white";
		
		// 클릭 이벤트 추가
		link.addEventListener("click", function(event) {
		    event.preventDefault();  // 링크의 기본 동작(페이지 이동)을 막습니다.
		    console.log("링크 클릭됨!");
			none_sliderLegend();
			
		    const clickedText = event.currentTarget.textContent;
		    let matchedPoint = interestPoints.find(point => point.name === clickedText);
			
			if (matchedPoint) {
				move_coor = matchedPoint.coordinates;
			    console.log(move_coor); // 일치하는 좌표 출력
			    defalut_lat = move_coor[0];
			    defalut_lot = move_coor[1] - 0.003;
			    
			    //initMap();
			    initMapAndDrawGrid();  
			} else {
			    console.log("일치하는 이름을 찾을 수 없습니다.");
			}
		});
		
		td11.appendChild(link);
        //td11.textContent = point.name;
        td11.style.textAlign = 'left';
        td11.dataset.coordinates = point.coordinates.join(','); // 좌표 데이터를 저장
		td11.style.padding = '5px';
		td11.style.paddingLeft = '10px';
        tr1.appendChild(td1);
        tr1.appendChild(td11);

        interestInnerTable.appendChild(tr1);
    });

	interestTd.appendChild(interestInnerTable);
	interestTr.appendChild(interestTd);
	interestTable.appendChild(interestTr);

	// 센서보기 슬라이더 부분을 위한 내부 테이블 생성
	const sensorInnerTable = document.createElement("table");
	const sensorTr = document.createElement("tr");
	const sensorTd = document.createElement("td");

    const sensorRow = document.createElement("tr");
    
	// "센서 보기" 라벨에 대한 td
	const sensorLabelCell = document.createElement("td");
	sensorLabelCell.style.width = "50%"; // 너비 설정
	sensorLabelCell.style.textAlign = "center";
	sensorLabelCell.style.padding = '10px';
	
	const sensorLabel = document.createElement("span");
	sensorLabel.textContent = "센서 확인";
	sensorLabelCell.appendChild(sensorLabel);
	
	// 슬라이더에 대한 td
	const sensorSliderCell = document.createElement("td");
	sensorSliderCell.style.width = "50%"; // 너비 설정
	sensorSliderCell.style.textAlign = "center";
	sensorSliderCell.style.padding = '10px';
	
	const sensorSlider = document.createElement('input');
	sensorSlider.style.width = '50%'; // td의 대부분을 차지하게 함
	sensorSlider.type = 'range';
	sensorSlider.id = 'sensorSlider';
	sensorSlider.min = '0';
	sensorSlider.max = '1';
	sensorSlider.step = '1';
	sensorSlider.value = '1';
	sensorSlider.title = 'sensorSlider';
	sensorSliderCell.appendChild(sensorSlider);
	
	sensorRow.appendChild(sensorLabelCell);
	sensorRow.appendChild(sensorSliderCell);
	sensorInnerTable.appendChild(sensorRow);
	sensorTd.appendChild(sensorInnerTable);
	sensorTr.appendChild(sensorTd);
	interestTable.appendChild(sensorTr);
    
    displaySensors(true);
    sensorSlider.addEventListener('input', function(e) {
        const showSensors = (e.target.value === "1");
        displaySensors(showSensors);
    });
}



function displaySensors(show) {
	let sensor_name;
	let sensor_lat;
	let sensor_lot;
	
    if (show) {
		fetch(`${baseUrl}/get_sensor_location`, { method: 'POST' }) 
		    .then(response => response.json()) 
		    .then(data => {
		        for (const key in data) {
		            if (data.hasOwnProperty(key)) {
		                sensor_name = data["01sensor_name"];
		                sensor_lat = data["02sensor_lat"];
		                sensor_lot = data["03sensor_lot"];
		            }
		        }
		        
		        console.log("sensor_name: ", sensor_name);
				
				// 센서 위치 그리기
				for(let i = 0; i < sensor_name.length; i++){
					let s_num = sensor_name[i];
					let s_lat = sensor_lat[i];
					let s_lot = sensor_lot[i];
					
			        const sensorCircle = new google.maps.Circle({
			            strokeColor: '#FFFFFF',
			            strokeOpacity: 1.0,
			            strokeWeight: 2.5,
			            fillColor: '#FFFFFF',
			            fillOpacity: 0.5,
			            map: map,
			            center: { lat: s_lat, lng: s_lot },
			            radius: 20
			        });
			        circles.push(sensorCircle);
			        
			        
					const infoWindow = new google.maps.InfoWindow({
					    maxWidth: 100,
					    zIndex: 1000
					});

    			    // 클릭 리스너 추가
				    google.maps.event.addListener(sensorCircle, 'click', function(event) {
					    const contentString = `
					    <div style="font-size:5px; font-weight:bold; padding-bottom: 10px; padding:5px; white-space:nowrap;">
					        센서 번호: WT${s_num}
					    </div>`;
					    
					    infoWindow.setContent(contentString);
				        infoWindow.setPosition(event.latLng);
				        infoWindow.open(map);
				    });  
				    
                    // 텍스트 오버레이 추가
                    const triangleSymbol = '●';
                    const textOverlay = new google.maps.OverlayView();
                    textOverlay.onAdd = function () {
                        const div = document.createElement('div');
                        div.style.position = 'absolute';
                        div.style.color = 'white';
                        div.style.fontSize = '20px';
                        div.style.fontWeight = 'bold';
                        div.style.zIndex = 998;
                        div.innerHTML = triangleSymbol;
                        this.div_ = div;
                        const panes = this.getPanes();
                        panes.overlayMouseTarget.appendChild(div);
                    };
                    textOverlay.draw = function () {
                        const overlayProjection = this.getProjection();
                        const center = sensorCircle.getCenter();
                        const position = overlayProjection.fromLatLngToDivPixel(center);
                        const div = this.div_;
                        div.style.left = position.x + -6 + 'px';
                        div.style.top = position.y + -14 + 'px';
                    };
                    textOverlay.onRemove = function () {
                        this.div_.parentNode.removeChild(this.div_);
                        this.div_ = null;
                    };
                    textOverlay.setMap(map);
                    
                    map.addListener('zoom_changed', function () {
					    const zoom = map.getZoom();
					    const radius = calculateRadius(zoom);
					    sensorCircle.setRadius(radius);
					});
					
					runnings.push(textOverlay);
				}
		    })
		    .catch(error => {
		        console.error('Error:', error);
		    });
    } else {
		clearSensorCircles(circles);
		clearRunningSensors(runnings);
    }
}

function calculateRadius(zoom) {
    // 확대/축소 수준에 따라 원하는 반경을 계산합니다.
    return 50 * Math.pow(2, (15 - zoom));
}

function fromLatLngToPixel2(lat, lng) {
    var scale = Math.pow(2, map.getZoom());
    var nw = new google.maps.LatLng(
        map.getBounds().getNorthEast().lat(),
        map.getBounds().getSouthWest().lng()
    );
    var worldCoordinateNW = map.getProjection().fromLatLngToPoint(nw);
    var worldCoordinate = map.getProjection().fromLatLngToPoint(new google.maps.LatLng(lat, lng));
    var pixelOffset = new google.maps.Point(
        Math.floor((worldCoordinate.x - worldCoordinateNW.x) * scale),
        Math.floor((worldCoordinate.y - worldCoordinateNW.y) * scale)
    );
    return pixelOffset;
}


function date_time_search() {
    const table = document.getElementById('dateTime');
    table.innerHTML = '';
    table.style.width = '100%';

    // 제일 위의 행 추가 (빨간색 border 표시)
    const trTop1 = document.createElement('tr');
    const tdTop1 = document.createElement('td');
    tdTop1.style.padding = '5px';
    tdTop1.style.borderBottom = '1px solid deepskyblue';
    trTop1.appendChild(tdTop1);
    table.appendChild(trTop1);

    // 그 다음의 행 추가
    const trTop2 = document.createElement('tr');
    const tdTop2 = document.createElement('td');
    tdTop2.style.padding = '5px';
    trTop2.appendChild(tdTop2);
    table.appendChild(trTop2);
    
    // 메인 테이블의 첫 번째 행: "날짜/시간 조회" 텍스트
    const trHead = document.createElement('tr');
    const tdHead = document.createElement('td');
    tdHead.textContent = "날짜/시간 조회";
    tdHead.style.textAlign = "left";
    tdHead.style.fontSize = "15px";
    tdHead.style.fontWeight = "bold";
    tdHead.style.padding = '10px';
    trHead.appendChild(tdHead);
    table.appendChild(trHead);

    // 메인 테이블의 두 번째 행: 내부 테이블을 포함
    const trMain = document.createElement('tr');
    const tdMain = document.createElement('td');
    const mainInnerTable = document.createElement('table');
    mainInnerTable.style.width = '100%';
	
    // 내부 테이블의 첫 번째 행: 날짜 및 시간 선택
    const trDate = document.createElement('tr');
    const tdDate = document.createElement('td');
    const dateTable = document.createElement('table');
    dateTable.style.width = '100%';
    
    const trDate_1 = document.createElement('tr');
    const tdDate_1 = document.createElement('td');
    tdDate_1.style.width = '100%';
	tdDate_1.style.padding = '10px';
	
	/*
	const dateLabel = document.createElement('label');
    dateLabel.textContent = '날짜';
    dateLabel.for = 'datePicker';
	*/
    
    const datePicker = document.createElement('input');
    datePicker.type = 'date';
    datePicker.id = 'datePicker';
    datePicker.title = '날짜';
	datePicker.style.fontSize = '12px';        // 폰트 크기 조절
	datePicker.style.textAlign = 'center';     // 가운데 정렬
	datePicker.style.backgroundColor = '#37538E';
	datePicker.style.color = 'white';
	datePicker.style.fontWeight = 'bold';
	datePicker.style.borderRadius = '5px';
	datePicker.style.border = '2px solid #37538E';
    //tdDate_1.appendChild(dateLabel);
    tdDate_1.appendChild(datePicker);

    const tdDate_2 = document.createElement('td');
    tdDate_2.style.width = '100%';
	tdDate_2.style.padding = '10px';
	
	/*
    const timeLabel = document.createElement('label');
    timeLabel.textContent = '시간';
    timeLabel.for = 'timePicker';
	*/
	
    const timePicker = document.createElement('input');
    timePicker.type = 'time';
    timePicker.id = 'timePicker';
    timePicker.title = '시간';
	timePicker.style.fontSize = '12px';        // 폰트 크기 조절
	timePicker.style.textAlign = 'center';     // 가운데 정렬
	//timePicker.setAttribute("placeholder", "시간:분");  // 플레이스홀더 설정 (모든 브라우저에서 동작하지 않을 수 있음)
	timePicker.style.backgroundColor = '#37538E';
	timePicker.style.color = 'white';
	timePicker.style.fontWeight = 'bold';
	timePicker.style.borderRadius = '5px';
	timePicker.style.border = '2px solid #37538E';
		
    //tdDate_2.appendChild(timeLabel);
    tdDate_2.appendChild(timePicker);

    trDate_1.appendChild(tdDate_1);
    trDate_1.appendChild(tdDate_2);
    dateTable.appendChild(trDate_1);
    tdDate.appendChild(dateTable);
    trDate.appendChild(tdDate);
    mainInnerTable.appendChild(trDate);

    // 내부 테이블의 두 번째 행: 검색 및 초기화 버튼
    const trButton = document.createElement('tr');
    const tdButton = document.createElement('td');
    const buttonTable = document.createElement('table');
    buttonTable.style.width = '100%';
	buttonTable.style.flex = '1';
	
    // 버튼 관련 코드 (검색 및 초기화 버튼을 추가)
    const trButton_1 = document.createElement('tr');
    const tdButton_1 = document.createElement('td');
    tdButton_1.style.width = '50%';

    const searchButton = document.createElement('button');
    searchButton.textContent = '검색';
    searchButton.style.width = '50%';
	searchButton.style.backgroundColor = '#0075ff';
	searchButton.style.color = 'white';
	searchButton.style.fontWeight = 'bold';
	searchButton.style.fontSize = '12px';
	searchButton.style.borderRadius = '5px';
	searchButton.style.border = '2px solid #03153A';
	
	searchButton.onclick = function() {
	    const date = document.getElementById('datePicker').value;
	    const time = document.getElementById('timePicker').value;
	    if (date && time) {
	        if (selectedCheckbox) { //관심지점 체크박스 선택 시
	            none_sliderLegend();
	            run_predict(date, time, selectedCoordinates);
	        } else {
	            //여기
	            none_sliderLegend();
	            run_predict(date, time, selectedCoordinates);
	            //alert("바람길 예측 시 장소를 선택해주세요.");
	        }
	    } else {
	        alert("날짜/시간을 선택해주세요.");
	    }
	};

    tdButton_1.appendChild(searchButton);
    trButton_1.appendChild(tdButton_1);

    const tdButton_2 = document.createElement('td');
    tdButton_2.style.width = '50%';

    const resetButton = document.createElement('button');
    resetButton.textContent = '초기화';
    resetButton.style.width = '50%';
	resetButton.style.backgroundColor = '#0075ff';
	resetButton.style.color = 'white';
	resetButton.style.fontWeight = 'bold';
	resetButton.style.fontSize = '12px';
	resetButton.style.borderRadius = '5px';
	resetButton.style.border = '2px solid #03153A';
	
	resetButton.onclick = function() {
	    none_sliderLegend();
	    clearRectangles(rectangles);
	    clearPolylines(polylines);
	    clearPredictPolylines(predict_polylines);
	    const datePicker = document.getElementById('datePicker');
	    const timePicker = document.getElementById('timePicker');
	    datePicker.value = '';
	    timePicker.value = '';
	    const resultDiv = document.getElementById('datetime-result');
	    if (resultDiv) {
	        resultDiv.innerHTML = '';
	    }
	};

    tdButton_2.appendChild(resetButton);
    trButton_1.appendChild(tdButton_2);

    buttonTable.appendChild(trButton_1);
    tdButton.appendChild(buttonTable);

    trButton.appendChild(tdButton);
    mainInnerTable.appendChild(trButton);

    tdMain.appendChild(mainInnerTable);
    trMain.appendChild(tdMain);
    table.appendChild(trMain);
}


function checkbox_intetest_point() {
    // 3행: 체크 박스와 장소명 표시
    const checkboxTable = document.getElementById("checkbox-interest-point");
    checkboxTable.innerHTML = '';
    checkboxTable.addEventListener('change', function(event) {
	    const selectedCheckbox = event.target;
		if (selectedCheckbox.type === 'checkbox' && !selectedCheckbox.checked) {
		    none_location = true;
		}
	    if (selectedCheckbox.type === 'checkbox' && selectedCheckbox.checked) {
			none_location = false;
	        const selectedPlaceName = selectedCheckbox.value;
	        const selectedInterestPoint = interestPoints.find(point => point.name === selectedPlaceName);
			
	        if (selectedInterestPoint) {
	            const coordinates = selectedInterestPoint.coordinates;
	            selectedCoordinates = coordinates;
	            //console.log(`선택한 관심지점(${selectedPlaceName})의 좌표: ${coordinates[0]}, ${coordinates[1]}`);
	        } else {
	            console.log(`선택한 관심지점(${selectedPlaceName})을 interestPoints에서 찾을 수 없습니다.`);
	        }
	    }
	});

    // 이전에 선택된 체크박스 요소를 저장할 변수
    //let selectedCheckbox = null;

    interestPoints.forEach(point => {
        const tr3 = document.createElement("tr");
        
        const td3 = document.createElement("td");
        const checkbox = document.createElement('input');
        
        td3.style.padding = '2px';
        td3.style.paddingTop = '8px';
        td3.style.paddingLeft = '5px';
        checkbox.style.transform = "scale(1.2)";
        checkbox.type = 'checkbox';
        checkbox.className = 'checkbox';
        checkbox.value = point.name; // 장소명을 checkbox의 값으로 설정
        checkbox.id = `checkbox-${point.name}`; // 고유한 ID 생성
        checkbox.addEventListener('change', function() {
            if (this.checked) {
                if (selectedCheckbox !== null) {
                    selectedCheckbox.checked = false;
                }
                selectedCheckbox = this;
            } else {
                selectedCheckbox = null;
            }
        });
        td3.appendChild(checkbox);

	    const label = document.createElement("label"); // 새로운 label 요소 생성
	    label.htmlFor = `checkbox-${point.name}`; // label과 checkbox를 연결
	    label.textContent = point.name; // 레이블 텍스트 설정

		const td33 = document.createElement("td");
        const circle1 = document.createElement("div");
        
        td33.style.padding = '2px';
        td33.style.paddingTop = '0px';
        circle1.className = `circle ${point.colorClass}`;
        td33.appendChild(circle1);
        
        const td333 = document.createElement("td");
        td333.style.padding = '2px';
        td333.style.paddingTop = '8px';
        td333.appendChild(label); // 레이블을 td 요소에 추가
        td333.style.textAlign = 'left';
        td333.dataset.coordinates = point.coordinates.join(','); // 좌표 데이터를 저장

        tr3.appendChild(td3);
        tr3.appendChild(td33);
        tr3.appendChild(td333);

        checkboxTable.appendChild(tr3);
    });   
    
    /*
    const predictTable = document.getElementById("predict-table");
    const p_tr = document.createElement("tr");
    const p_div = document.createElement("div");
    p_div.id = "predict-status";
    p_div.textContent = "상태 확인용";
    p_tr.appendChild(p_div);
    predictTable.appendChild(p_tr);
    */
}

	
window.onload = async function() {
    var modal = document.getElementById('predictSettingsModal');
    var settingsLink = document.getElementById('settingsLink');
    var closeBtn = document.querySelector('.close');
    var modalContent = document.getElementById('modalContent');
	let input;
	
    settingsLink.onclick = function (event) {
        event.preventDefault();  // 기본 동작 방지
        modal.style.display = 'block';
    }

    closeBtn.onclick = function () {
        modal.style.display = 'none';
    }

    window.onclick = function (event) {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    }

	const variableNames = [
    "격좌 좌상단 좌표",
    "격자 우하단 좌표",
    "격자 간격(m)",
    "DB 저장 날짜/시간",
    "센서 선택 방식",
    "주변 센서 개수",
    "센서 반경(m)",
    //"예측 시작 위치",
    //"예측 시작 날짜/시간",
    "모델링 간격(개수)",
    "마지막 센서 번호",
    "모델링 간격(시간)",
    "정규분포(번)",
    "클러스터링 여부",
    "n분 전"
	];
	
	try {
		let response = await fetch(`${baseUrl}/setting_code`, { method: 'POST' });
		let data = await response.json();
		
        const upper_left = data["01upper_left"];
        const lower_right = data["02lower_right"];
        const grid_size = data["03grid_size"];
        const start_time = data["04start_time"];
        let sensor_method = data["05sensor_method"]; // 0: 개수, 1: 반경
        let sensor_count = data["06sensor_count"];
  		let sensor_radius = data["07sensor_radius"];
        //const start_point = data["08start_point"];
        //const prediction_start_time = data["09prediction_start_time"];
        const interval = data["10interval"];
        const sensor_num = data["11sensor_num"];
        const interval_time = data["12interval_time"];
        let normal_distribution = data["13normal_distribution"];
        let cluster_method = data["14cluster_method"]; // 0: 아니오, 1: 예(기본)
        let m_before = data["15m_before"];
        
		grid_space = grid_size;
		modelingNum = interval;
		modelingSec = interval_time;
		normalDist = normal_distribution;
		n_minute = m_before;
		
		// 각 데이터 값을 배열에 저장하기 전에 변환
		sensor_method = sensor_method === 0 ? '개수' : '반경';
		cluster_method = cluster_method === 0 ? '아니오' : '예(기본)';

		// 각 데이터 값을 배열에 저장
		let values = [
		    upper_left,
		    lower_right,
		    grid_space,
		    start_time,
		    sensor_method,
		    sensor_count,
		    sensor_radius,
		    //start_point,
		    //prediction_start_time,
		    modelingNum,
		    sensor_num,
		    modelingSec,
		    normalDist,
		    cluster_method,
		    n_minute
		];
		
		// 각 값의 변화를 서버에 저장하는 함수
		async function saveChanges() {
		    try {
		        let response = await fetch(`${baseUrl}/edit_settings`, {
		            method: 'POST',
		            headers: {
		                'Content-Type': 'application/json'
		            },
		            body: JSON.stringify({
		                "sensor_method": sensor_method,
		                "cluster_method": cluster_method,
		                "sensor_count": sensor_count,
		                "sensor_radius": sensor_radius,
		                "normal_distribution": normal_distribution,
		                "n_minute": n_minute
		            })
		        });
		        let data = await response.json();
		        let checking = data["01result"]
		        console.log("checking: ", checking);
		    } catch (error) {
		        console.error('Error:', error);
		    }
		}

        // 모달 내용을 지우기
        modalContent.innerHTML = "";
	        
	    
		// 테이블 생성
		let table = document.createElement("table");
		let tbody = document.createElement("tbody");

		table.style.width = '100%';
		table.style.borderCollapse = 'collapse';
		table.style.border = '2px solid black';

		// 각 변수 이름과 값으로 테이블 행 생성
		for (let i = 0; i < variableNames.length; i++) {
		    let tr = document.createElement("tr");
		
		    let td1 = document.createElement("td");
		    td1.textContent = variableNames[i];
		    td1.style.border = '1px solid black';
		    td1.style.padding = '5px';
		    td1.style.fontSize = '12px';
		    td1.style.fontWeight = 'bold';
		    
		    tr.appendChild(td1);
		
		    let td2 = document.createElement("td");
		    
	        function handleCheckboxChange(event, valueType) {
	            if (valueType === "sensor_method") {
	                sensor_method = event.target.checked ? 1 : 0;
	            } else if (valueType === "cluster_method") {
	                cluster_method = event.target.checked ? 1 : 0;
	            }
	        }
	
	        function handleInputChange(event, valueType) {
	            if (valueType === "sensor_count") {
	                sensor_count = event.target.value;
	            } else if (valueType === "sensor_radius") {
	                sensor_radius = event.target.value;
	            } else if (valueType === "normal_distribution") {
	                normal_distribution = event.target.value;
	            } else if (valueType === "n_minute") {
					n_minute = event.target.value;
				}
	        }
	        
		    function updateCheckboxText(checkbox, span, onText, offText) {
		        if (checkbox.checked) {
		            span.textContent = onText;
		        } else {
		            span.textContent = offText;
		        }
		    }
	
		    if (variableNames[i] === "센서 선택 방식") {
		        let checkbox = document.createElement("input");
		        checkbox.type = "checkbox";
		        checkbox.checked = sensor_method === "반경";
		
		        let span = document.createElement("span");
		        span.textContent = checkbox.checked ? " 반경(기본)" : " 개수";
		        checkbox.addEventListener("change", (e) => {
		            handleCheckboxChange(e, "sensor_method");
		            updateCheckboxText(checkbox, span, " 반경(기본)", " 개수");
		        });
		        td2.appendChild(checkbox);
		        td2.appendChild(span);
		    } else if (variableNames[i] === "클러스터링 여부") {
		        let checkbox = document.createElement("input");
		        checkbox.type = "checkbox";
		        checkbox.checked = cluster_method === "예(기본)";
		
		        let span = document.createElement("span");
		        span.textContent = checkbox.checked ? " 예(기본)" : " 아니오";
		        checkbox.addEventListener("change", (e) => {
		            handleCheckboxChange(e, "cluster_method");
		            updateCheckboxText(checkbox, span, " 예(기본)", " 아니오");
		        });
		        td2.appendChild(checkbox);
		        td2.appendChild(span);
		    }  else if (variableNames[i] === "주변 센서 개수" || variableNames[i] === "센서 반경(m)" || variableNames[i] === "정규분포(번)" || variableNames[i] === "n분 전") {
	            input = document.createElement("input");
	            input.type = "number";
	            input.value = values[i];
	            input.style.width = '70px';
	            input.style.textAlign = 'center';
	            if (variableNames[i] === "센서 선택 방식") {
	                input.addEventListener("change", (e) => {
						handleInputChange(e, "sensor_count");
						saveChanges();
	                });
	            } else if (variableNames[i] === "센서 반경(m)") {
	                input.addEventListener("change", (e) => {
						handleInputChange(e, "sensor_radius");
						saveChanges();
					});
	            } else if (variableNames[i] === "정규분포(번)") {
	                input.addEventListener("change", (e) => {
						handleInputChange(e, "normal_distribution");
						saveChanges();
					});
	            } else if (variableNames[i] === "n분 전") {
					input.addEventListener("change", (e) => {
						handleInputChange(e, "n_minute");
						saveChanges();
					});
				}
	            td2.appendChild(input);
	        } else {
	            td2.textContent = values[i];
	        }

		    td2.style.border = '1px solid black';
		    td2.style.fontSize = '12px';
		    td2.style.padding = '5px';
		    tr.appendChild(td2);
		
		    tbody.appendChild(tr);
		}
		
		table.appendChild(tbody);
		modalContent.appendChild(table);
    } catch (error){
		consoloe.error('Error: ', error);
	}
};

async function run_predict(date, time, selectedCoordinates) {
    predictDateTime = formatDateTime(date, time);
    
    let latlng;
    if(selectedCoordinates != null) {
	    predictCoordinates = formatCoordinates(selectedCoordinates);
    
	    latlng = [predictCoordinates[1], predictCoordinates[0]];
	    predictLineList.length = 0;
	    predictLineList.push(latlng);
	}

    try {
		let response = await fetch(`${baseUrl}/get_exist_dateTime`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({ "predictDateTime": predictDateTime })
		});
		let data = await response.json();
		let exist_dateTime = data["01existDateTime"]; 
		let exist_before = data["02existBefore"]; 
		
		console.log("response: ", response.status);
		console.log("Server data:", data);
		console.log("exist_dateTime: ", exist_dateTime);
		
		// 관심지점 선택 ㅇ
		if(exist_dateTime > 0 && exist_before > 0 && predictCoordinates != null){
		    console.log(predictDateTime);
		    console.log(predictCoordinates);
		    
		    // 예측 실행
		    // "실행 중" 메시지를 표시
		    const statusDiv1 = document.getElementById('predict-status');
		    //statusDiv1.textContent = "실행 중...";
		    //statusDiv1.textContent = "Loading...";
			//statusDiv1.style.color = "red";
			statusDiv1.style.display = "flex";
			
			response = await fetch(`${baseUrl}/windpath_predict_code`, {
			    method: 'POST',
			    headers: {
			        'Content-Type': 'application/json'
			    },
		
			    body: JSON.stringify({ "predictDateTime": predictDateTime, "predictCoordinates": predictCoordinates })
			});
			data = await response.json();
			
			exist_id = data["01exist_id"];
			t_n = data["02max_value"];
			
			if(exist_id >= 0){
				/*
				response = await fetch(`${baseUrl}/get_first_cmap`, { method: 'POST' });
				data = await response.json();
				
				let first_t_n = data["04first_t_n"];
				console.log("first_t_n: ", first_t_n);
				*/
				//test_function();
				updateTable();
				if (none_location == false){
					sliderLegend(); //
				}
				//statusDiv1.textContent = "실행 완료";
				//statusDiv1.textContent = "fin.";
				//statusDiv1.style.color = "deepskyblue";
				statusDiv1.style.display = "none";
				
				console.log('예측 정상 실행.'); // 서버에서 반환한 결과 출력
				console.log('exist_id: ', exist_id, ', t_n: ', t_n);
			}	
		}
		if(exist_dateTime > 0 && exist_before > 0 && none_location == true){
		    // 풍속 풍향 
		    // "실행 중" 메시지를 표시
		    const statusDiv1 = document.getElementById('predict-status');
		    //statusDiv1.textContent = "실행 중...";
		    //statusDiv1.textContent = "Loading...";
			//statusDiv1.style.color = "red";
			statusDiv1.style.display = "flex";
			
			response = await fetch(`${baseUrl}/wind_speed_direction`, {
			    method: 'POST',
			    headers: {
			        'Content-Type': 'application/json'
			    },
		
			    body: JSON.stringify({ "predictDateTime": predictDateTime })
			});
			data = await response.json();
			
			no_m_name = data["01m_name"];
			no_center_lot = data["02center_lot"];
			no_center_lat = data["03center_lat"];
			no_wd = data["04wd"];
			no_ws = data["05ws"];
			
			console.log("**wd: ", no_wd);
			
	        var my_slider = document.getElementById('mySlider');
	        var slider_table = document.getElementById('inner-table-slider');
	        
	        my_slider.min = 1;
	        max11 = no_m_name.length + 1;
	        my_slider.max = max11;
	        my_slider.value = max11;
	        //슬라이더 설정하고
	        visitedValues = new Set();
	        visitedValues.add(max11);
	        
	        slider_table.innerHTML = '';
	        my_tr = document.createElement("tr");
	        
	        for(let i = no_m_name.length - 1; i >=0; i--){
				f_t_n = i;
				
				my_td = document.createElement("td");
				my_td.id = "predict-t-" + f_t_n; 
				cal = (i+1) * n_minute;
				my_td.textContent = cal + "분 전"; 
				my_tr.appendChild(my_td);
			}
			my_td = document.createElement("td");
			my_td.id = "predict-t-11"; 
			my_td.textContent = "예측 시작"; 
			my_tr.appendChild(my_td);
			
	        slider_table.appendChild(my_tr);
	        
	        sliderLegend();
			//statusDiv1.textContent = "fin.";
			//statusDiv1.style.color = "deepskyblue";
			statusDiv1.style.display = "none";
		}
		if(exist_dateTime <= 0 && exist_before <= 0) {
			alert("DB에 해당 날짜/시간이 존재하지 않습니다.")
		}
	} catch (error) {
			console.error('Error:', error);
	}
}

function sliderLegend(){
	var slider = document.getElementById('mySlider');
	slider.value = max11;
	
    const container1 = document.getElementById('contain-slider');
    if (container1.style.display === "none" || container1.style.display === "") {
        container1.style.display = "block";
    }
    
    const container2 = document.getElementById('legend-slider');
    if (container2.style.display === "none" || container2.style.display === "") {
        container2.style.display = "block";
    }
    
	const seeLegend = document.getElementById('see-legend');
	seeLegend.addEventListener('input', function(e){
	    const rows = document.querySelectorAll('#legend-table tr');
	    if (e.target.value == 1) {
	        rows[0].style.display = '';
	        rows[1].style.display = '';
	    } else if (e.target.value == 0) {
	        rows[0].style.display = 'none';
	        rows[1].style.display = 'none';
	    }
	});
}

function none_sliderLegend(){
    var slider = document.getElementById('mySlider');
    slider.value = max11;
    if(slider.value == max11){
		clearRectangles(rectangles);
		clearPolylines(polylines);
		clearPredictPolylines(predict_polylines);
	}
				
    const container1 = document.getElementById('contain-slider');
    if (container1.style.display === "block") {
        container1.style.display = "none";
    }
    
    const container2 = document.getElementById('legend-slider');
    if (container2.style.display === "block") {
		container2.style.display = "none";
    }
}

function t_n_before(){
	
}

// 날짜와 시간을 받아서 원하는 형식으로 변환하는 함수
function formatDateTime(date, time) {
    const formattedDate = new Date(`${date}T${time}`);
    const formattedTime = formattedDate.toTimeString().slice(0, 8);
    const formattedDateTime = `${formattedDate.getFullYear()}-${padZero(formattedDate.getMonth() + 1)}-${padZero(formattedDate.getDate())} ${formattedTime}`;
    return formattedDateTime;
}

// 한 자릿수의 숫자를 두 자릿수로 변환하는 함수
function padZero(number) {
    return number.toString().padStart(2, '0');
}
// 좌표를 받아서 원하는 형식으로 변환하는 함수
function formatCoordinates(coordinates) {
	if (coordinates && coordinates.length === 2) {
	    const formattedCoordinates = [coordinates[1], coordinates[0]];
    	return formattedCoordinates;
	}
	else {
		return null;
	}
}


async function usingSlider(predict_t_n){
	if (none_location == true) {
		clearPolylines(polylines);
	
		response = await fetch(`${baseUrl}/get_sensor_data1`, { method: 'POST' });
		data = await response.json();
		let p_lat = data["01lat_list"]; //오름차순
		let p_lot = data["02lot_list"];
		
		let width = p_lot.length - 1;
		let height = p_lat.length - 1;
		let start = width * height - width + 1;
		
		//console.log("width: ", width, ", height: ", height, ", start: ", start);
		
		let cluster_grid = []; // 그리드 번호 부여
		for (let row = 0; row < height; row++) {
			if (row % 2 === 0) {//짝수행
				cluster_grid.push(Array.from({ length: width }, (_, index) => start + index));
			} else {
				cluster_grid.push(Array.from({ length: width }, (_, index) => start + width - 1 - index).reverse());
			}
			start -= width;
		}
		
		//console.log("cluster_grid: ", cluster_grid);
		
		let center_grids = []; // 3x3 중심 그리드 번호
		for (let row = 1; row < height; row += 3) {
			for (let col = 1; col < width; col += 3) {
				let center_grid = row * width + col + 1;
				center_grids.push(center_grid);
			}
		}
		
		//console.log("center_grids: ", center_grids);
	    const statusDiv1 = document.getElementById('predict-status');
		//statusDiv1.textContent = "풍속/풍향 그리기 실행 중...";
		//statusDiv1.textContent = "Loading...";
		//statusDiv1.style.color = "red";
		statusDiv1.style.display = "flex";
		
		let con2;
		function condition2(k){
			if (grid_space <= 50){
				con2 = center_grids.includes(k + 1);
			}
			else {
				con2 = true;
			}
			return con2;
		}
			
		console.log("predict_t_n: ", predict_t_n);
		
		if(predict_t_n != max11){
			// 풍속/풍향 그리기
			for (let k = 0; k < no_m_name[predict_t_n].length; k++) {
				
				//console.log("no_center_lat: ", no_center_lat[predict_t_n]);
				if (condition2(k)) {
					
					//console.log("진입확인");
					let center_num = k + 1;
					//console.log("center_num: ", center_num);
					//console.log("p_m_name2: ", p_m_name2);
					
					let center_index = no_m_name[predict_t_n].indexOf(center_num);
					//console.log("**center_index: ", center_index);
					
					let latitude = no_center_lat[predict_t_n][center_index];
					let longitude = no_center_lot[predict_t_n][center_index];
					
					let direction = no_wd[predict_t_n][center_index];
					let speed = no_ws[predict_t_n][center_index];
					
					let vector_x = -1 * Math.cos(Math.PI * (direction / 180)) * (0.0002 * speed);
					let vector_y = -1 * Math.sin(Math.PI * (direction / 180)) * (0.0002 * speed);
					
					let x = latitude + vector_x;
					let y = longitude + vector_y;
					
					if (!isNaN(x) && !isNaN(y)) {
					    let line_list = [
					        {lat: latitude, lng: longitude},
					        {lat: x, lng: y}
					    ];
						
						//console.log("line_list: ", line_list);
					
					    let arrowSymbol = {
					        path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW,
					        scale: 1.8
					    };
					    
						let polylineOptions = {
							path: line_list,
							strokeColor: 'white',
							strokeOpacity: 1,
							strokeWeight: 2,
							zIndex: 998,
					        icons: [{
					            icon: arrowSymbol,
					            offset: '100%'
					        }]
						};
						
						let polyline = new google.maps.Polyline(polylineOptions);
						polyline.setMap(map);
						polylines.push(polyline);
					}
				}	
			}
		}
		//statusDiv1.textContent = "fin.";
		//statusDiv1.style.color = "deepskyblue";
		statusDiv1.style.display = "none";
	}		
	else if (predict_t_n <= first_t_n.length) {
		clearRectangles(rectangles);
		clearPolylines(polylines);
		clearPredictPolylines(predict_polylines);
		
		try {
			let response = await fetch(`${baseUrl}/get_sensor_data2`, { method: 'POST' });
			let data = await response.json();
			let p_all_grid_num = data["01grid_num"];

			console.log("p_all_grid_num: ", p_all_grid_num);

			response = await fetch(`${baseUrl}/get_cmap_data1`, { method: 'POST' });
			data = await response.json();
			let p_t = data["01max_t"];

			response = await fetch(`${baseUrl}/get_sensor_data3`, { method: 'POST' }); 
			data = await response.json();
			let p_grid_num3 = data["01grid_num"];
			let p_gen_time3 = data["02gen_time"];
			let upper_left_lot = data["03upper_left_lot"];
			let upper_left_lat = data["04upper_left_lat"];
			let upper_right_lot = data["05upper_right_lot"];
			let upper_right_lat = data["06upper_right_lat"];
			let lower_right_lot = data["07lower_right_lot"];
			let lower_right_lat = data["08lower_right_lat"];
			let lower_left_lot = data["09lower_left_lot"];
			let lower_left_lat = data["10lower_left_lat"];
			let center_lot = data["11center_lot"];
			let center_lat = data["12center_lat"];
			let p_section3 = data["13section"];

			response = await fetch(`${baseUrl}/get_sensor_data1`, { method: 'POST' });
			data = await response.json();
			let p_lat = data["01lat_list"]; //오름차순
			let p_lot = data["02lot_list"];

			response = await fetch(`${baseUrl}/get_cmap_data2`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ "predict_t_n": predict_t_n, "exist_id": exist_id })
			});
			data = await response.json();
			
			let p_grid_num1 = data["01grid_num"]; 
			let p_normal_num1 = data["02normal_num"]; //normal_num 기준 내림차순
			let p_date1 = data["03date"];
			let p_t_n1 = data["04t_n"];
			let p_id1 = data["05id"];
			
			console.log("p_normal_num1: ", p_normal_num1);
			
			//let max_index = p_normal_num1.indexOf(Math.max(...p_normal_num1));
			let grid_date = p_date1[0]; // grid_date:  2023-04-11 11:28:03
			
			console.log("* grid_date: ", grid_date);
			
			response = await fetch(`${baseUrl}/get_estimate_data1`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ "grid_date": grid_date })
			});
			data = await response.json();
			let p_m_id2 = data["01m_id"];
			let p_m_name2 = data["02m_name"]; //m_name 즉 그리드 번호 기준 오름차순
			let p_center_lot2 = data["03center_lot"];
			let p_center_lat2 = data["04center_lat"];
			let p_wd2 = data["05wd"];
			let p_ws2 = data["06ws"];
			let p_vec_x2 = data["07vec_x"];
			let p_vec_y2 = data["08vec_y"];
			let p_date2 = data["09date"];
			
			//console.log("p_lot: ", p_lot.length, ", p_lat: ", p_lat.length);

			let width = p_lot.length - 1;
			let height = p_lat.length - 1;
			let start = width * height - width + 1;
			
			//console.log("width: ", width, ", height: ", height, ", start: ", start);
			
			let cluster_grid = []; // 그리드 번호 부여
			for (let row = 0; row < height; row++) {
				if (row % 2 === 0) {//짝수행
					cluster_grid.push(Array.from({ length: width }, (_, index) => start + index));
				} else {
					cluster_grid.push(Array.from({ length: width }, (_, index) => start + width - 1 - index).reverse());
				}
				start -= width;
			}
			
			//console.log("cluster_grid: ", cluster_grid);
			
			let center_grids = []; // 3x3 중심 그리드 번호
			for (let row = 1; row < height; row += 3) {
				for (let col = 1; col < width; col += 3) {
					let center_grid = row * width + col + 1;
					center_grids.push(center_grid);
				}
			}
			
			//console.log("center_grids: ", center_grids);
		    const statusDiv1 = document.getElementById('predict-status');
			//statusDiv1.textContent = "풍속/풍향 그리기 실행 중...";
			//statusDiv1.textContent = "Loading...";
			//statusDiv1.style.color = "red";
			statusDiv1.style.display = "flex";
			
			let con2;
			function condition2(k){
				if (grid_space <= 50){
					con2 = center_grids.includes(k + 1);
				}
				else {
					con2 = true;
				}
				return con2;
			}
			

			// 풍속/풍향 그리기
			for (let k = 0; k < p_all_grid_num; k++) {
				if (condition2(k)) {
						
					let center_num = k + 1;
					//console.log("center_num: ", center_num);
					//console.log("p_m_name2: ", p_m_name2);
					
					let center_index = p_m_name2.indexOf(center_num);
					//console.log("**center_index: ", center_index);
					
					let latitude = p_center_lat2[center_index];
					let longitude = p_center_lot2[center_index];
					
					let direction = p_wd2[center_index];
					let speed = p_ws2[center_index];
					
					let vector_x = -1 * Math.cos(Math.PI * (direction / 180)) * (0.0002 * speed);
					let vector_y = -1 * Math.sin(Math.PI * (direction / 180)) * (0.0002 * speed);
					
					let x = latitude + vector_x;
					let y = longitude + vector_y;
					
					if (!isNaN(x) && !isNaN(y)) {
					    let line_list = [
					        {lat: latitude, lng: longitude},
					        {lat: x, lng: y}
					    ];
						
						//console.log("line_list: ", line_list);
					
					    let arrowSymbol = {
					        path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW,
					        scale: 1.8
					    };
					    
						let polylineOptions = {
							path: line_list,
							strokeColor: 'white',
							strokeOpacity: 1,
							strokeWeight: 2,
							zIndex: 998,
					        icons: [{
					            icon: arrowSymbol,
					            offset: '100%'
					        }]
						};
						
						let polyline = new google.maps.Polyline(polylineOptions);
						polyline.setMap(map);
						polylines.push(polyline);
					}
				}	
			}
			
			//statusDiv1.textContent = "분포 색상 그리기 실행 중...";
			//statusDiv1.textContent = "Loading...";
			//statusDiv1.style.color = "red";
			statusDiv1.style.display = "flex";
			
			let cmap_list = [];
			
			// 색상 정규화
			response = await fetch(`${baseUrl}/get_colormap`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ "p_grid_num1": p_grid_num1,  "p_normal_num1": p_normal_num1})
			});
			data = await response.json();
			cmap_color1 = data["01color_list"];

			
			// 분포 색상 그리기
			for (let i = 0; i < p_grid_num1.length; i++) {
				let num = p_grid_num1[i];
				let grid_data_index = p_grid_num3.indexOf(num);
				
				let rectangleCoords = [
					{'lat': lower_left_lat[grid_data_index], 'lng': lower_left_lot[grid_data_index]},
					{'lat': lower_right_lat[grid_data_index], 'lng': lower_right_lot[grid_data_index]},
					{'lat': upper_right_lat[grid_data_index], 'lng': upper_right_lot[grid_data_index]},
					{'lat': upper_left_lat[grid_data_index], 'lng': upper_left_lot[grid_data_index]}
				]
				
				cmap_color2 = cmap_color1[i];
				
				let rectangleOptions = {
					paths: rectangleCoords,
					strokeOpacity: 0.0,
					strokeWeight: 1,
					fillColor: cmap_color2,
					fillOpacity: 0.8,
					zIndex: 999,
				};
				
				let rectangle = new google.maps.Polygon(rectangleOptions);
				rectangle.setMap(map);
				rectangles.push(rectangle);
			}
			//statusDiv1.textContent = "그리기 실행 완료.";
			//statusDiv1.textContent = "fin.";
			//statusDiv1.style.color = "deepskyblue";
			statusDiv1.style.display = "none";
			
			console.log("rectangles: ", rectangles.length);
		} catch (error) {
			console.error('Error:', error);
		}
	}
	if(predict_t_n == max11 || predict_t_n > max11) {
		clearRectangles(rectangles);
		clearPolylines(polylines);
		clearPredictPolylines(predict_polylines);
	}
	console.log("시각화 확인");
}

function clearRunningSensors(runnings){
    for (let running of runnings) {
        running.setMap(null);
    }
    running = [];  // 배열을 비워둠
}

function clearSensorCircles(circles){
    // 원들을 지도에서 제거
    for (let circle of circles) {
        circle.setMap(null);
    }
    circles = [];  // 배열을 비워둠
}

function clearRectangles(rectangles){
    for(let i = 0; i < rectangles.length; i++){
        rectangles[i].setMap(null); // remove the rectangle from the map
    }
    rectangles.length = 0; 
}

function clearPolylines(polylines){
    for(let i = 0; i < polylines.length; i++){
        polylines[i].setMap(null); // remove the rectangle from the map
    }
    polylines.length = 0; 
}

async function updateTable() {
	try {
		let response = await fetch(`${baseUrl}/get_first_cmap`, { method: 'POST' });
		let data = await response.json();
		
		first_grid_num = data["01first_grid_num"];
        first_normal_num = data["02first_normal_num"];
        first_date = data["03first_date"];
        first_t_n = data["04first_t_n"];
        first_id = data["05first_id"];
        
		console.log("first_t_n: ", first_t_n);
        var my_slider = document.getElementById('mySlider');
        var slider_table = document.getElementById('inner-table-slider');
        
        console.log("first_t_n: ", first_t_n); //--
        
        my_slider.min = 1;
        max11 =first_t_n.length + 1;
        my_slider.max = max11;
        my_slider.value = max11;
        //슬라이더 설정하고
        visitedValues = new Set();
        visitedValues.add(max11);
        
        slider_table.innerHTML = '';
        my_tr = document.createElement("tr");
        
        for(let i = first_t_n.length - 1; i >=0; i--){
			f_t_n = i;
			
			my_td = document.createElement("td");
			my_td.id = "predict-t-" + f_t_n; 
			cal = (i+1) * n_minute;
			my_td.textContent = cal + "분 전"; 
			my_tr.appendChild(my_td);
		}
		my_td = document.createElement("td");
		my_td.id = "predict-t-11"; 
		my_td.textContent = "예측 시작"; 
		my_tr.appendChild(my_td);
		
        slider_table.appendChild(my_tr);
	} catch (error){
		console.error('Error:', error);
	}
}

async function drawPredictLine(predict_t_n){
	console.log("predict_t_n:", predict_t_n); //[0,1]->0 or 1
	
	if(none_location == true){
		first_t_n = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9];
	}
	
	if (predict_t_n <= first_t_n.length && none_location == false) {
		try {
		    const statusDiv1 = document.getElementById('predict-status');
			//statusDiv1.textContent = "Loading...";
			//statusDiv1.style.color = "red";
			statusDiv1.style.display = "flex";
			
			//table2에 연결해서 해당 date, grid_num일 때의 lat, lot 얻어오기
			 d_index = first_t_n.indexOf(predict_t_n);
			 d_grid_num = first_grid_num[d_index];
			 d_normal_num = first_normal_num[d_index];
			 d_date = first_date[d_index];

			let response = await fetch(`${baseUrl}/get_predict_line`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ "d_date": d_date, "d_grid_num": d_grid_num })
			});
			let data = await response.json();
			
			let d_lat = data["01center_lat"];
			let d_lot = data["02center_lot"];
			
			let d_latlng = [d_lat, d_lot]; 
			predictLineList.push(d_latlng);
			
			clearPredictPolylines(predict_polylines);
			
			let coor = [predictCoordinates[1], predictCoordinates[0]]; //[위도, 경도]
			//console.log("predictCoordinates: ", [predictCoordinates[1], predictCoordinates[0]]);
			//console.log("coor: ", coor);
			
			let selected = interestPoints.find(point => point.coordinates[0] === coor[0] && point.coordinates[1] === coor[1]);
			console.log("selected: ", selected);
            let selectedColor = selected.colorClass;
            //console.log("selectedColor: ", selectedColor);
            
			const getColorFromClass = (className, property) => {
			    // 임시 div 요소 생성
			    const div = document.createElement('div');
			    div.className = className;  // 해당 CSS 클래스 설정
			    document.body.appendChild(div);  // 임시로 body에 추가
			
			    // 계산된 스타일에서 색상값 가져오기
			    const color = window.getComputedStyle(div).getPropertyValue(property);
			    
			    // 임시 div 요소 제거
			    document.body.removeChild(div);
			    return color.trim();
			};
			
			let selectedColorValue = getColorFromClass(selectedColor, 'background-color');

            let newList = predictLineList.slice(0, predict_t_n + 2);
            console.log("predictLineList: ", predictLineList);
            console.log("newList: ", newList);
            
			let pathCoordinates = newList.map(predictLine => ({ lat: predictLine[0], lng: predictLine[1] }));
			

			//예측선 그리기
		    let polyline = new google.maps.Polyline({
		        path: pathCoordinates,
		        geodesic: true,
		        strokeColor: selectedColorValue,
		        strokeOpacity: 1.0,
		        strokeWeight: 6,
		        zIndex: 1001,
		    });
		    
		    polyline.setMap(map);
		    predict_polylines.push(polyline);			
		} catch (error){
			console.error('Error:', error);
		}
	}
}

function clearPredictPolylines(predict_polylines){
    for(let i = 0; i < predict_polylines.length; i++){
        predict_polylines[i].setMap(null); // remove the rectangle from the map
    }
    predict_polylines.length = 0; 
}
