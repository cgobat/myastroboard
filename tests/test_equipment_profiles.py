"""
Tests for Equipment Profiles Module
"""
import pytest
import os
import json
import tempfile
from datetime import datetime
import sys
import types

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import equipment_profiles


@pytest.fixture
def temp_data_dir(monkeypatch):
    """Create a temporary data directory for testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.setenv('DATA_DIR', tmpdir)
        # Recreate the module-level EQUIPMENT_DIR with new temp path
        equipment_profiles.EQUIPMENT_DIR = os.path.join(tmpdir, 'equipments')
        yield tmpdir


@pytest.fixture
def test_user_id():
    """Provide a test user ID"""
    return "test-user-123"


# ============================================================
# Telescope Tests
# ============================================================

def test_create_telescope(temp_data_dir, test_user_id):
    """Test creating a telescope profile"""
    telescope_data = {
        'name': 'Test Refractor',
        'telescope_type': 'Refractor',
        'aperture_mm': 102,
        'focal_length_mm': 714,
        'reducer_barlow_factor': 0.8,
        'notes': 'My first scope'
    }
    
    telescope = equipment_profiles.create_telescope(test_user_id, telescope_data)
    
    assert telescope is not None
    assert telescope['name'] == 'Test Refractor'
    assert telescope['aperture_mm'] == 102
    assert telescope['focal_length_mm'] == 714
    assert telescope['native_focal_ratio'] == 7.0  # 714 / 102
    assert telescope['effective_focal_length'] == 571.2  # 714 * 0.8
    assert telescope['effective_focal_ratio'] == 5.6  # 571.2 / 102
    assert 'id' in telescope
    assert 'created_at' in telescope


def test_get_telescope(temp_data_dir, test_user_id):
    """Test retrieving a telescope profile"""
    telescope_data = {
        'name': 'Test SCT',
        'telescope_type': 'Schmidt-Cassegrain (SCT)',
        'aperture_mm': 203,
        'focal_length_mm': 2032,
        'reducer_barlow_factor': 0.63
    }
    
    created = equipment_profiles.create_telescope(test_user_id, telescope_data)
    retrieved = equipment_profiles.get_telescope(test_user_id, created['id'])
    
    assert retrieved is not None
    assert retrieved['id'] == created['id']
    assert retrieved['name'] == 'Test SCT'


def test_update_telescope(temp_data_dir, test_user_id):
    """Test updating a telescope profile"""
    telescope_data = {
        'name': 'Old Name',
        'telescope_type': 'Refractor',
        'aperture_mm': 80,
        'focal_length_mm': 400,
        'reducer_barlow_factor': 1.0
    }
    
    created = equipment_profiles.create_telescope(test_user_id, telescope_data)
    
    update_data = {
        'name': 'New Name',
        'telescope_type': 'Refractor',
        'aperture_mm': 80,
        'focal_length_mm': 480,  # Changed
        'reducer_barlow_factor': 1.0,
        'notes': 'Updated notes'
    }
    
    updated = equipment_profiles.update_telescope(test_user_id, created['id'], update_data)
    
    assert updated is not None
    assert updated['name'] == 'New Name'
    assert updated['focal_length_mm'] == 480
    assert updated['notes'] == 'Updated notes'


def test_delete_telescope(temp_data_dir, test_user_id):
    """Test deleting a telescope profile"""
    telescope_data = {
        'name': 'To Delete',
        'telescope_type': 'Newtonian',
        'aperture_mm': 200,
        'focal_length_mm': 1000,
        'reducer_barlow_factor': 1.0
    }
    
    created = equipment_profiles.create_telescope(test_user_id, telescope_data)
    success = equipment_profiles.delete_telescope(test_user_id, created['id'])
    
    assert success is True
    
    # Verify it's gone
    retrieved = equipment_profiles.get_telescope(test_user_id, created['id'])
    assert retrieved is None


# ============================================================
# Camera Tests
# ============================================================

def test_create_camera(temp_data_dir, test_user_id):
    """Test creating a camera profile"""
    camera_data = {
        'name': 'ASI294MC Pro',
        'manufacturer': 'ZWO',
        'sensor_width_mm': 19.1,
        'sensor_height_mm': 13.0,
        'resolution_width_px': 4144,
        'resolution_height_px': 2822,
        'pixel_size_um': 4.63,
        'sensor_type': 'CMOS Color',
        'cooling_supported': True,
        'min_temperature_c': -10,
        'read_noise_e': 3.8,
        'quantum_efficiency': 80
    }
    
    camera = equipment_profiles.create_camera(test_user_id, camera_data)
    
    assert camera is not None
    assert camera['name'] == 'ASI294MC Pro'
    assert camera['sensor_diagonal_mm'] > 0  # Should be calculated
    assert camera['cooling_supported'] is True
    assert camera['min_temperature_c'] == -10


def test_camera_diagonal_calculation(temp_data_dir, test_user_id):
    """Test that camera diagonal is correctly calculated"""
    camera_data = {
        'name': 'Test Camera',
        'manufacturer': 'Test',
        'sensor_width_mm': 3.0,
        'sensor_height_mm': 4.0,  # 3-4-5 triangle
        'resolution_width_px': 1920,
        'resolution_height_px': 1080,
        'pixel_size_um': 5.0,
        'sensor_type': 'CMOS Mono'
    }
    
    camera = equipment_profiles.create_camera(test_user_id, camera_data)
    
    # Diagonal should be 5.0 (3-4-5 triangle)
    assert camera['sensor_diagonal_mm'] == 5.0


# ============================================================
# Mount Tests
# ============================================================

def test_create_mount(temp_data_dir, test_user_id):
    """Test creating a mount profile"""
    mount_data = {
        'name': 'EQ6-R Pro',
        'mount_type': 'Equatorial',
        'payload_capacity_kg': 20,
        'tracking_accuracy_arcsec': 1.5,
        'guiding_supported': True
    }
    
    mount = equipment_profiles.create_mount(test_user_id, mount_data)
    
    assert mount is not None
    assert mount['name'] == 'EQ6-R Pro'
    assert mount['payload_capacity_kg'] == 20
    assert mount['recommended_payload_kg'] == 15.0  # 75% of 20
    assert mount['guiding_supported'] is True


# ============================================================
# Filter Tests
# ============================================================

def test_create_filter(temp_data_dir, test_user_id):
    """Test creating a filter profile"""
    filter_data = {
        'name': 'H-Alpha 7nm',
        'filter_type': 'Narrowband',
        'central_wavelength_nm': 656.3,
        'bandwidth_nm': 7,
        'intended_use': 'Emission nebulae imaging'
    }
    
    filter_obj = equipment_profiles.create_filter(test_user_id, filter_data)
    
    assert filter_obj is not None
    assert filter_obj['name'] == 'H-Alpha 7nm'
    assert filter_obj['central_wavelength_nm'] == 656.3
    assert filter_obj['bandwidth_nm'] == 7


# ============================================================
# FOV Calculator Tests
# ============================================================

def test_fov_calculation():
    """Test Field of View calculation"""
    # Example: 80mm refractor f/6 with ASI294MC Pro
    fov = equipment_profiles.calculate_fov(
        telescope_focal_length_mm=480,
        camera_sensor_width_mm=19.1,
        camera_sensor_height_mm=13.0,
        camera_pixel_size_um=4.63,
        seeing_arcsec=2.0
    )
    
    assert fov.horizontal_fov_deg > 0
    assert fov.vertical_fov_deg > 0
    assert fov.diagonal_fov_deg > 0
    assert fov.image_scale_arcsec_per_px > 0
    assert fov.sampling_classification in ['Undersampled', 'Optimal', 'Oversampled']


def test_fov_sampling_classification():
    """Test FOV sampling classification"""
    # Undersampled case (large image scale - pixels too big for seeing)
    # Need: image_scale > seeing/2 (i.e., > 1.0 for 2" seeing)
    # Formula: image_scale = 206.265 * pixel_um/1000 / focal_mm
    # For undersampling: use very large pixels (webcam) with very short FL
    fov_under = equipment_profiles.calculate_fov(
        telescope_focal_length_mm=1.2,  # Extremely short FL (unrealistic but for testing)
        camera_sensor_width_mm=10,
        camera_sensor_height_mm=10,
        camera_pixel_size_um=6,  # Typical webcam pixel size
        seeing_arcsec=2.0
    )
    # Image scale = 206.265 * 6/1000 / 1.2 = 1.03 arcsec/px
    # Optimal max = 2/2 = 1.0, so 1.03 > 1.0 = Undersampled
    assert fov_under.sampling_classification == 'Undersampled'
    
    # Optimal case (optimal sampling for seeing)
    # Need: seeing/3 < image_scale < seeing/2 (i.e., 0.67 to 1.0 for 2" seeing)
    fov_optimal = equipment_profiles.calculate_fov(
        telescope_focal_length_mm=1000,
        camera_sensor_width_mm=10,
        camera_sensor_height_mm=10,
        camera_pixel_size_um=3.76,
        seeing_arcsec=2.0
    )
    # Image scale = 206.265 * 3.76/1000 / 1000 = 0.78 arcsec/px
    # Optimal range: 0.67 to 1.0, so 0.78 is in range = Optimal
    assert fov_optimal.sampling_classification == 'Optimal'
    
    # Oversampled case (small image scale - pixels too small for seeing)
    # Need: image_scale < seeing/3 (i.e., < 0.67 for 2" seeing)
    fov_over = equipment_profiles.calculate_fov(
        telescope_focal_length_mm=3000,
        camera_sensor_width_mm=10,
        camera_sensor_height_mm=10,
        camera_pixel_size_um=2.4,  # Small pixels
        seeing_arcsec=2.0
    )
    # Image scale = 206.265 * 2.4/1000 / 3000 = 0.165 arcsec/px
    # Optimal min = 2/3 = 0.67, so 0.165 < 0.67 = Oversampled
    assert fov_over.sampling_classification == 'Oversampled'


# ============================================================
# Equipment Combination Tests
# ============================================================

def test_create_combination(temp_data_dir, test_user_id):
    """Test creating an equipment combination"""
    # Create some equipment first
    telescope = equipment_profiles.create_telescope(test_user_id, {
        'name': 'Test Scope',
        'telescope_type': 'Refractor',
        'aperture_mm': 102,
        'focal_length_mm': 714,
        'reducer_barlow_factor': 1.0
    })
    
    camera = equipment_profiles.create_camera(test_user_id, {
        'name': 'Test Camera',
        'manufacturer': 'Test',
        'sensor_width_mm': 13.2,
        'sensor_height_mm': 8.8,
        'resolution_width_px': 3096,
        'resolution_height_px': 2080,
        'pixel_size_um': 4.5,
        'sensor_type': 'CMOS Color'
    })
    
    combination_data = {
        'name': 'My Imaging Setup',
        'telescope_id': telescope['id'],
        'camera_id': camera['id'],
        'notes': 'Primary deep-sky setup'
    }
    
    combination = equipment_profiles.create_combination(test_user_id, combination_data)
    
    assert combination is not None
    assert combination['name'] == 'My Imaging Setup'
    assert combination['telescope_id'] == telescope['id']
    assert combination['camera_id'] == camera['id']


def test_combination_requires_telescope_or_camera(temp_data_dir, test_user_id):
    """Test that combination requires at least telescope or camera"""
    combination_data = {
        'name': 'Invalid Setup',
        # No telescope_id or camera_id
    }
    
    combination = equipment_profiles.create_combination(test_user_id, combination_data)
    
    # Should fail because neither telescope nor camera is specified
    assert combination is None


def test_analyze_combination(temp_data_dir, test_user_id):
    """Test analyzing an equipment combination"""
    # Create telescope and camera
    telescope = equipment_profiles.create_telescope(test_user_id, {
        'name': 'Refractor 102/714',
        'telescope_type': 'Refractor',
        'aperture_mm': 102,
        'focal_length_mm': 714,
        'reducer_barlow_factor': 0.8
    })
    
    camera = equipment_profiles.create_camera(test_user_id, {
        'name': 'ASI294MC Pro',
        'manufacturer': 'ZWO',
        'sensor_width_mm': 19.1,
        'sensor_height_mm': 13.0,
        'resolution_width_px': 4144,
        'resolution_height_px': 2822,
        'pixel_size_um': 4.63,
        'sensor_type': 'CMOS Color'
    })
    
    combination = equipment_profiles.create_combination(test_user_id, {
        'name': 'Wide-Field Setup',
        'telescope_id': telescope['id'],
        'camera_id': camera['id']
    })
    
    analysis = equipment_profiles.analyze_combination(test_user_id, combination['id'])
    
    assert analysis is not None
    assert analysis.combination_id == combination['id']
    assert analysis.telescope is not None
    assert analysis.camera is not None
    assert analysis.fov_calculation is not None
    assert len(analysis.suitability) > 0  # Should have at least one suitability
    assert len(analysis.recommendations) > 0  # Should have recommendations


def test_equipment_summary(temp_data_dir, test_user_id):
    """Test getting equipment summary"""
    # Create some equipment
    equipment_profiles.create_telescope(test_user_id, {
        'name': 'Scope 1',
        'telescope_type': 'Refractor',
        'aperture_mm': 80,
        'focal_length_mm': 400,
        'reducer_barlow_factor': 1.0
    })
    
    equipment_profiles.create_camera(test_user_id, {
        'name': 'Camera 1',
        'manufacturer': 'Test',
        'sensor_width_mm': 10,
        'sensor_height_mm': 10,
        'resolution_width_px': 1920,
        'resolution_height_px': 1080,
        'pixel_size_um': 5.0,
        'sensor_type': 'CMOS'
    })
    
    summary = equipment_profiles.get_all_equipment_summary(test_user_id)
    
    assert summary['telescopes_count'] == 1
    assert summary['cameras_count'] == 1
    assert summary['mounts_count'] == 0
    assert summary['filters_count'] == 0
    assert summary['combinations_count'] == 0


# ============================================================
# Safety Tests
# ============================================================

def test_safe_save_creates_backup(temp_data_dir, test_user_id):
    """Test that safe save creates backups"""
    # Create initial data
    telescope_data = {
        'name': 'Original',
        'telescope_type': 'Refractor',
        'aperture_mm': 80,
        'focal_length_mm': 400,
        'reducer_barlow_factor': 1.0
    }
    
    equipment_profiles.create_telescope(test_user_id, telescope_data)
    
    file_path = equipment_profiles.get_user_equipment_file(test_user_id, 'telescopes')
    assert os.path.exists(file_path)
    
    # Update should use safe save
    data = equipment_profiles.load_user_telescopes(test_user_id)
    success = equipment_profiles.save_user_telescopes(test_user_id, data)
    
    assert success is True
    # Backup should be cleaned up after successful save
    backup_path = file_path + '.backup'
    assert not os.path.exists(backup_path)


def test_update_and_delete_camera_mount_filter_accessory_and_combination(temp_data_dir, test_user_id):
    camera = equipment_profiles.create_camera(
        test_user_id,
        {
            'name': 'Cam A',
            'manufacturer': 'Maker',
            'sensor_width_mm': 13.2,
            'sensor_height_mm': 8.8,
            'resolution_width_px': 3000,
            'resolution_height_px': 2000,
            'pixel_size_um': 3.8,
            'sensor_type': 'CMOS Color',
            'min_temperature_c': '',
            'read_noise_e': '',
            'quantum_efficiency': '',
        },
    )
    assert camera is not None

    updated_camera = equipment_profiles.update_camera(
        test_user_id,
        camera['id'],
        {
            'name': 'Cam B',
            'manufacturer': 'Maker',
            'sensor_width_mm': 13.2,
            'sensor_height_mm': 8.8,
            'resolution_width_px': 3100,
            'resolution_height_px': 2100,
            'pixel_size_um': 3.8,
            'sensor_type': 'CMOS Color',
            'cooling_supported': True,
            'is_shared': True,
        },
    )
    assert updated_camera is not None
    assert updated_camera['name'] == 'Cam B'

    mount = equipment_profiles.create_mount(
        test_user_id,
        {
            'name': 'Mount A',
            'mount_type': 'Equatorial',
            'payload_capacity_kg': 12,
            'tracking_accuracy_arcsec': '',
            'guiding_supported': True,
        },
    )
    assert mount is not None
    updated_mount = equipment_profiles.update_mount(
        test_user_id,
        mount['id'],
        {
            'name': 'Mount B',
            'mount_type': 'Equatorial',
            'payload_capacity_kg': 14,
            'tracking_accuracy_arcsec': 1.2,
            'guiding_supported': True,
            'is_shared': True,
        },
    )
    assert updated_mount is not None
    assert updated_mount['recommended_payload_kg'] == 10.5

    filt = equipment_profiles.create_filter(
        test_user_id,
        {
            'name': 'Filter A',
            'filter_type': 'Narrowband',
            'central_wavelength_nm': 656.3,
            'bandwidth_nm': 7,
            'is_shared': True,
        },
    )
    assert filt is not None
    updated_filter = equipment_profiles.update_filter(
        test_user_id,
        filt['id'],
        {
            'name': 'Filter B',
            'filter_type': 'Narrowband',
            'central_wavelength_nm': '',
            'bandwidth_nm': '',
            'is_shared': False,
        },
    )
    assert updated_filter is not None
    assert updated_filter['name'] == 'Filter B'

    accessory = equipment_profiles.create_accessory(
        test_user_id,
        {
            'name': 'Focuser',
            'manufacturer': 'X',
            'accessory_type': 'Focuser',
            'weight_kg': '',
            'is_shared': True,
        },
    )
    assert accessory is not None
    updated_accessory = equipment_profiles.update_accessory(
        test_user_id,
        accessory['id'],
        {
            'name': 'Focuser Pro',
            'manufacturer': 'X',
            'accessory_type': 'Focuser',
            'weight_kg': 0.3,
            'is_shared': False,
        },
    )
    assert updated_accessory is not None
    assert updated_accessory['name'] == 'Focuser Pro'

    scope = equipment_profiles.create_telescope(
        test_user_id,
        {
            'name': 'Scope',
            'telescope_type': 'Refractor',
            'aperture_mm': 80,
            'focal_length_mm': 480,
            'reducer_barlow_factor': 1.0,
        },
    )
    combo = equipment_profiles.create_combination(
        test_user_id,
        {
            'name': 'Combo A',
            'telescope_id': scope['id'],
            'camera_id': camera['id'],
            'mount_id': mount['id'],
            'filter_ids': [filt['id']],
            'accessory_ids': [accessory['id']],
        },
    )
    assert combo is not None

    updated_combo = equipment_profiles.update_combination(
        test_user_id,
        combo['id'],
        {
            'name': 'Combo B',
            'telescope_id': scope['id'],
            'camera_id': camera['id'],
            'mount_id': mount['id'],
            'filter_ids': [],
            'accessory_ids': [],
        },
    )
    assert updated_combo is not None
    assert updated_combo['name'] == 'Combo B'

    assert equipment_profiles.delete_combination(test_user_id, combo['id']) is True
    assert equipment_profiles.delete_accessory(test_user_id, accessory['id']) is True
    assert equipment_profiles.delete_filter(test_user_id, filt['id']) is True
    assert equipment_profiles.delete_mount(test_user_id, mount['id']) is True
    assert equipment_profiles.delete_camera(test_user_id, camera['id']) is True


def test_load_helpers_return_defaults_on_invalid_json(temp_data_dir, test_user_id):
    pairs = [
        ('cameras', equipment_profiles.load_user_cameras),
        ('mounts', equipment_profiles.load_user_mounts),
        ('filters', equipment_profiles.load_user_filters),
        ('accessories', equipment_profiles.load_user_accessories),
        ('combinations', equipment_profiles.load_user_combinations),
    ]
    for eq_type, loader in pairs:
        p = equipment_profiles.get_user_equipment_file(test_user_id, eq_type)
        with open(p, 'w', encoding='utf-8') as f:
            f.write('{invalid json')
        loaded = loader(test_user_id)
        assert isinstance(loaded, dict)
        assert isinstance(loaded.get('items', []), list)


def test_shared_equipment_and_combination_status(temp_data_dir, monkeypatch):
    user_a = 'owner-a'
    user_b = 'viewer-b'

    fake_auth = types.SimpleNamespace(
        user_manager=types.SimpleNamespace(
            list_users=lambda: [
                {'user_id': user_a, 'username': 'alice'},
                {'user_id': user_b, 'username': 'bob'},
            ]
        )
    )
    monkeypatch.setitem(sys.modules, 'auth', fake_auth)

    tel_file = equipment_profiles.get_user_equipment_file(user_a, 'telescopes')
    cam_file = equipment_profiles.get_user_equipment_file(user_a, 'cameras')
    combo_file = equipment_profiles.get_user_equipment_file(user_a, 'combinations')

    with open(tel_file, 'w', encoding='utf-8') as f:
        json.dump({'items': [{'id': 't1', 'name': 'Scope', 'is_shared': True}]}, f)
    with open(cam_file, 'w', encoding='utf-8') as f:
        json.dump({'items': [{'id': 'c1', 'name': 'Cam', 'is_shared': True}]}, f)
    with open(combo_file, 'w', encoding='utf-8') as f:
        json.dump(
            {
                'items': [
                    {
                        'id': 'combo1',
                        'name': 'Shared Combo',
                        'telescope_id': 't1',
                        'camera_id': 'c1',
                        'mount_id': None,
                        'filter_ids': [],
                        'accessory_ids': [],
                    }
                ]
            },
            f,
        )

    shared_tel = equipment_profiles.load_all_shared_equipment('telescopes', exclude_user_id=user_b)
    assert len(shared_tel) == 1
    assert shared_tel[0]['owner_username'] == 'alice'

    status_ok = equipment_profiles.compute_combination_share_status(
        {
            'telescope_id': 't1',
            'camera_id': 'c1',
            'mount_id': None,
            'filter_ids': [],
            'accessory_ids': [],
        },
        user_a,
    )
    assert status_ok['is_shared'] is True
    assert status_ok['has_broken_share'] is False

    status_broken = equipment_profiles.compute_combination_share_status(
        {
            'telescope_id': 'missing',
            'camera_id': None,
            'mount_id': None,
            'filter_ids': [],
            'accessory_ids': [],
        },
        user_b,
    )
    assert status_broken['is_shared'] is False
    assert status_broken['has_broken_share'] is True
    assert status_broken['broken_items'] == ['missing']

    shared_combos = equipment_profiles.load_all_shared_combinations(exclude_user_id=user_b)
    assert len(shared_combos) == 1
    assert shared_combos[0]['owner_username'] == 'alice'


def test_safe_save_equipment_returns_false_when_validation_fails(tmp_path):
    target = tmp_path / 'equipment.json'
    target.write_text(json.dumps({'items': []}), encoding='utf-8')

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(equipment_profiles, 'validate_equipment_json', lambda _p: (False, 'bad'))
        ok = equipment_profiles.safe_save_equipment(str(target), {'items': []})

    assert ok is False


def test_analyze_combination_handles_missing_specs_and_missing_combination(temp_data_dir, test_user_id):
    # Missing combination id path
    assert equipment_profiles.analyze_combination(test_user_id, 'does-not-exist') is None

    telescope = equipment_profiles.create_telescope(
        test_user_id,
        {
            'name': 'Scope Missing Details',
            'telescope_type': 'Refractor',
            'aperture_mm': 80,
            'focal_length_mm': 480,
            'reducer_barlow_factor': 1.0,
        },
    )

    combo = equipment_profiles.create_combination(
        test_user_id,
        {
            'name': 'Partial Combo',
            'telescope_id': telescope['id'],
            'camera_id': None,
        },
    )
    analysis = equipment_profiles.analyze_combination(test_user_id, combo['id'])
    assert analysis is not None
    assert len(analysis.recommendations) > 0
