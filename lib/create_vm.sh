#!/bin/bash
# Create VM using OCI CLI
oci compute instance launch \
    --compartment-id ocid1.tenancy.oc1..aaaaaaaayrs62ecstfuwyipp6rpkz6oy3hdaimkpmab4wqtt3crpnsspubkq \
    --display-name "hasan-worker-vm" \
    --shape "VM.Standard.A1.Flex" \
    --shape-config '{"ocpus":4,"memoryInGBs":24}' \
    --image-id ocid1.image.oc1.eu-frankfurt-1.aaaaaaaapjjt7iczbhfml4ew6yo3hrxg4dzqrhbnsmwpd3uk6hvqqvjfz3q \
    --assign-public-ip true \
    --metadata '{"ssh_authorized_keys":"'"$(cat /data/data/com.termux/files/home/.ssh/id_ed25519.pub)"'"}' \
    --availability-domain "$(oci iam availability-domain list --compartment-id ocid1.tenancy.oc1..aaaaaaaayrs62ecstfuwyipp6rpkz6oy3hdaimkpmab4wqtt3crpnsspubkq --query 'data[0].name' --raw-output)" \
    --subnet-id "$(oci network subnet list --compartment-id ocid1.tenancy.oc1..aaaaaaaayrs62ecstfuwyipp6rpkz6oy3hdaimkpmab4wqtt3crpnsspubkq --query 'data[0].id' --raw-output)"
