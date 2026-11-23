extends Node3D

const BLOCKS := 5
const SPACING := 58.0
const ROAD_W := 15.0
var vehicle: CharacterBody3D
var vehicle_mesh: Node3D
var camera: Camera3D
var speed := 0.0
var steer := 0.0
var throttle := false
var brake := false
var left := false
var right := false
var bike_mode := false
var night := false
var hud: Label
var speed_label: Label
var vehicle_button: Button
var sun: DirectionalLight3D

func _ready() -> void:
	_build_world()
	_build_vehicle()
	_build_camera()
	_build_hud()
	Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)

func _mat(color: Color, rough := 0.85) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.albedo_color = color
	m.roughness = rough
	return m

func _box(parent: Node3D, pos: Vector3, size: Vector3, color: Color) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	var mesh := BoxMesh.new()
	mesh.size = size
	mi.mesh = mesh
	mi.position = pos
	mi.material_override = _mat(color)
	parent.add_child(mi)
	return mi

func _build_world() -> void:
	var env := WorldEnvironment.new()
	var e := Environment.new()
	e.background_mode = Environment.BG_SKY
	e.sky = Sky.new()
	e.sky.sky_material = ProceduralSkyMaterial.new()
	e.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	e.ambient_light_color = Color(0.68, 0.72, 0.78)
	e.ambient_light_energy = 0.65
	env.environment = e
	add_child(env)
	sun = DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-48, -32, 0)
	sun.light_energy = 1.15
	add_child(sun)
	_box(self, Vector3(0,-0.7,0), Vector3(420,1,420), Color(0.25,0.38,0.24))
	# Asphalt grid with painted lane lines.
	for i in range(-BLOCKS, BLOCKS + 1):
		var p := float(i) * SPACING
		_box(self, Vector3(p, -0.12, 0), Vector3(ROAD_W,0.18,410), Color(0.105,0.115,0.13))
		_box(self, Vector3(0, -0.115, p), Vector3(410,0.18,ROAD_W), Color(0.105,0.115,0.13))
		for z in range(-190,191,12):
			_box(self, Vector3(p,0.0,float(z)), Vector3(0.22,0.035,5.0), Color(0.88,0.78,0.43))
		for x in range(-190,191,12):
			_box(self, Vector3(float(x),0.0,p), Vector3(5.0,0.035,0.22), Color(0.88,0.78,0.43))
	# Dense blocks of varied Delhi-inspired shops and apartments.
	var colors := [Color("#c8a27c"),Color("#d9c6a5"),Color("#b7a28c"),Color("#c4b7a0"),Color("#a9b2ad"),Color("#d0b28e")]
	var rng := RandomNumberGenerator.new()
	rng.seed = 4317
	for gx in range(-BLOCKS, BLOCKS):
		for gz in range(-BLOCKS, BLOCKS):
			var cx := (float(gx)+0.5)*SPACING
			var cz := (float(gz)+0.5)*SPACING
			for j in range(3):
				var x := cx + rng.randf_range(-17,17)
				var z := cz + rng.randf_range(-17,17)
				var h := rng.randf_range(8,27)
				var w := rng.randf_range(8,15)
				var d := rng.randf_range(8,15)
				var b := _box(self, Vector3(x,h/2,z), Vector3(w,h,d), colors[rng.randi_range(0,colors.size()-1)])
				# rooftop parapet / water tank detail
				if rng.randf() > 0.45:
					_box(self, Vector3(x,h+1.0,z), Vector3(3,2.0,3), Color(0.34,0.38,0.4))
				# dark shopfront / windows facing a random street side
				var face := _box(self, Vector3(x,h*0.36,z-d*0.501), Vector3(w*0.55,2.0,0.12), Color(0.18,0.29,0.34))
	# Roadside trees and streetlights.
	for i in range(-4,5):
		for z in range(-170,171,42):
			var x := float(i)*SPACING + ROAD_W*0.68
			_box(self, Vector3(x,2.0,float(z)), Vector3(0.7,4,0.7), Color(0.31,0.2,0.12))
		var crown := MeshInstance3D.new()
		var sphere := SphereMesh.new()
		sphere.radius = 2.4
		sphere.height = 4.8
		crown.mesh = sphere
		crown.position = Vector3(x,5.0,float(z))
		crown.material_override = _mat(Color(0.15,0.34,0.19))
		add_child(crown)
	# landmark: metro station sign
	_box(self, Vector3(16,3,-44), Vector3(13,5,0.5), Color(0.04,0.32,0.28))
	var sign := Label3D.new()
	sign.text = "DELHI METRO  •  CITY CENTRE"
	sign.font_size = 48
	sign.position = Vector3(16,3,-43.6)
	sign.modulate = Color.WHITE
	add_child(sign)
	# static traffic vehicles for atmosphere
	for k in range(18):
		var car := Node3D.new()
		car.position = Vector3(-160 + float(k)*18,0.45, -25 if k%2==0 else 25)
		add_child(car)
		_box(car, Vector3.ZERO, Vector3(3.3,1.1,5.8), [Color("#d6d9d7"),Color("#b83c32"),Color("#d2a52f"),Color("#34495e")][k%4])
		_box(car, Vector3(0,0.75,-0.2), Vector3(2.7,0.8,2.8), Color("#263744"))

func _build_vehicle() -> void:
	vehicle = CharacterBody3D.new()
	vehicle.position = Vector3(0,0.8,8)
	add_child(vehicle)
	vehicle_mesh = Node3D.new()
	vehicle.add_child(vehicle_mesh)
	_make_vehicle_visual()

func _make_vehicle_visual() -> void:
	for c in vehicle_mesh.get_children(): c.queue_free()
	if bike_mode:
		_box(vehicle_mesh, Vector3(0,0.75,0), Vector3(0.65,0.65,2.2), Color("#c62828"))
		_box(vehicle_mesh, Vector3(0,1.25,-0.35), Vector3(0.7,0.55,0.8), Color("#25282b"))
		_box(vehicle_mesh, Vector3(0,1.25,0.55), Vector3(0.48,0.45,0.65), Color("#d7d9d8"))
		for z in [-0.85,0.85]:
			var wheel := MeshInstance3D.new()
			var cyl := CylinderMesh.new()
			cyl.top_radius = 0.48; cyl.bottom_radius = 0.48; cyl.height = 0.18
			wheel.mesh = cyl; wheel.rotation_degrees.z = 90; wheel.position = Vector3(0,0.48,z); wheel.material_override = _mat(Color("#151719")); vehicle_mesh.add_child(wheel)
	else:
		_box(vehicle_mesh, Vector3(0,0.85,0), Vector3(2.05,0.85,4.0), Color("#bd332b"))
		_box(vehicle_mesh, Vector3(0,1.52,-0.35), Vector3(1.72,0.75,2.0), Color("#263a49"))
		for x in [-1.05,1.05]:
			for z in [-1.35,1.35]:
				var wheel := MeshInstance3D.new()
				var cyl := CylinderMesh.new(); cyl.top_radius=0.42; cyl.bottom_radius=0.42; cyl.height=0.25
				wheel.mesh=cyl; wheel.rotation_degrees.z=90; wheel.position=Vector3(x,0.48,z); wheel.material_override=_mat(Color("#111315")); vehicle_mesh.add_child(wheel)

func _build_camera() -> void:
	camera = Camera3D.new()
	camera.current = true
	camera.fov = 72
	add_child(camera)
	camera.position = Vector3(0,5,14)

func _build_hud() -> void:
	var layer := CanvasLayer.new(); add_child(layer)
	var panel := PanelContainer.new(); panel.position=Vector2(18,16); panel.size=Vector2(300,88); layer.add_child(panel)
	var vb := VBoxContainer.new(); panel.add_child(vb)
	hud=Label.new(); hud.text="DELHI DRIVE  |  FREE ROAM\nExplore the city • No limits"; hud.add_theme_font_size_override("font_size",20); vb.add_child(hud)
	speed_label=Label.new(); speed_label.text="0 km/h  •  CAR"; speed_label.add_theme_font_size_override("font_size",18); vb.add_child(speed_label)
	var switch := Button.new(); switch.text="SWITCH CAR / BIKE"; switch.position=Vector2(18,118); switch.size=Vector2(220,58); layer.add_child(switch); switch.pressed.connect(_switch_vehicle)
	var day := Button.new(); day.text="DAY / NIGHT"; day.position=Vector2(250,118); day.size=Vector2(170,58); layer.add_child(day); day.pressed.connect(_toggle_night)
	_add_control(layer,"▲",Vector2(112,560),Vector2(90,90),func(v): throttle=v)
	_add_control(layer,"▼",Vector2(112,650),Vector2(90,65),func(v): brake=v)
	_add_control(layer,"◀",Vector2(18,625),Vector2(90,90),func(v): left=v)
	_add_control(layer,"▶",Vector2(206,625),Vector2(90,90),func(v): right=v)
	var note := Label.new(); note.text="Touch controls   •   Landscape recommended"; note.position=Vector2(18,205); note.add_theme_font_size_override("font_size",16); layer.add_child(note)

func _add_control(layer: CanvasLayer, caption: String, pos: Vector2, sz: Vector2, setter: Callable) -> void:
	var b := Button.new(); b.text=caption; b.position=pos; b.size=sz; b.add_theme_font_size_override("font_size",30); layer.add_child(b)
	b.button_down.connect(func(): setter.call(true))
	b.button_up.connect(func(): setter.call(false))

func _switch_vehicle() -> void:
	bike_mode = not bike_mode
	_make_vehicle_visual()
	speed_label.text = "%.0f km/h  •  %s" % [abs(speed)*3.6, "BIKE" if bike_mode else "CAR"]

func _toggle_night() -> void:
	night = not night
	sun.light_energy = 0.12 if night else 1.15
	sun.light_color = Color(0.55,0.62,0.85) if night else Color.WHITE
	var env := get_node_or_null("WorldEnvironment") as WorldEnvironment
	if env and env.environment:
		env.environment.background_color = Color("#101a31") if night else Color("#79a9d1")

func _physics_process(delta: float) -> void:
	var accel := 24.0 if not bike_mode else 19.0
	var max_speed := 34.0 if not bike_mode else 29.0
	if throttle: speed = move_toward(speed,max_speed,accel*delta)
	elif brake: speed = move_toward(speed,-10.0,accel*delta)
	else: speed = move_toward(speed,0.0,8.0*delta)
	var steer_input := float(right)-float(left)
	var turn_rate := 1.55 if not bike_mode else 1.9
	if abs(speed)>0.4:
		vehicle.rotate_y(-steer_input*turn_rate*delta*sign(speed)*clamp(abs(speed)/7.0,0.25,1.0))
	var forward := -vehicle.global_transform.basis.z
	vehicle.velocity.x = forward.x*speed
	vehicle.velocity.z = forward.z*speed
	vehicle.velocity.y = 0
	vehicle.move_and_slide()
	vehicle.position.y = 0.8
	var target := vehicle.global_position + vehicle.global_transform.basis * Vector3(0,4.6,11.5)
	camera.global_position = camera.global_position.lerp(target,delta*5.0)
	camera.look_at(vehicle.global_position + Vector3(0,1.2,0),Vector3.UP)
	speed_label.text = "%.0f km/h  •  %s" % [abs(speed)*3.6, "MOTORCYCLE" if bike_mode else "CAR"]

func _unhandled_key_input(event: InputEvent) -> void:
	if event is InputEventKey:
		if event.keycode == KEY_W or event.keycode == KEY_UP: throttle=event.pressed
		if event.keycode == KEY_S or event.keycode == KEY_DOWN: brake=event.pressed
		if event.keycode == KEY_A or event.keycode == KEY_LEFT: left=event.pressed
		if event.keycode == KEY_D or event.keycode == KEY_RIGHT: right=event.pressed
