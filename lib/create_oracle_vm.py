#!/usr/bin/env python3
"""
CREATE ORACLE VM — Creates a free tier ARM VM.
"""
import json
import oci
from oci.core import ComputeClient
from oci.core.models import LaunchInstanceDetails, CreateVnicDetails, SourceDetails

with open('/data/data/com.termux/files/home/.config/antidetect-creds/oracle.json') as f:
    creds = json.load(f)

oci_config = {
    "user": creds['user_ocid'],
    "fingerprint": creds['fingerprint'],
    "tenancy": creds['tenancy_ocid'],
    "region": creds['region'],
    "key_file": creds['key_file']
}

# SSH key for VM
with open('/data/data/com.termux/files/home/.ssh/id_ed25519.pub') as f:
    ssh_key = f.read().strip()

compute = ComputeClient(oci_config)

# Find Ubuntu image
print("🔍 Finding Ubuntu image...")
# Use a known stable Ubuntu image
image_id = "ocid1.image.oc1.eu-frankfurt-1.aaaaaaaapjjt7iczbhfml4ew6yo3hrxg4dzqrhbnsmwpd3uk6hvqqvjfz3q"  # Ubuntu 22.04 minimal

launch_details = LaunchInstanceDetails(
    display_name="hasan-worker-vm",
    compartment_id=creds['tenancy_ocid'],
    shape="VM.Standard.A1.Flex",
    shape_config=oci.core.models.LaunchInstanceShapeConfigDetails(
        ocpus=4,
        memory_in_gbs=24,
    ),
    source_details=SourceDetails(
        source_type="image",
        image_id=image_id,
    ),
    create_vnic_details=CreateVnicDetails(
        subnet_id=None,  # Will use default
        assign_public_ip=True,
    ),
    metadata={
        "ssh_authorized_keys": ssh_key,
    },
)

print("🚀 Creating VM...")
try:
    response = compute.launch_instance(launch_details)
    instance = response.data
    print(f"✅ VM Created!")
    print(f"   ID: {instance.id}")
    print(f"   State: {instance.lifecycle_state}")
    print(f"   Shape: {instance.shape}")
except Exception as e:
    print(f"❌ Failed: {e}")
