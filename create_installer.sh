#!/usr/bin/bash

main() {
    declare_variables
    purge_the_app
    delete_the_old_files
    create_a_new_executable_file
    package_the_tool
    create_installer
    start_the_installer
    print_info_message "Installation complete."
}

print_info_message() {
    echo -e "\e[1;34m[INFO]\e[0m $1"
}

declare_variables() {
    app_name="netscout"
    version="0.1.0"
    username=$USER
    build_dirs=("dist" "build" "package")
    installer="${app_name}.deb"
    package_base_dir="package"
    package_opt_dir="$package_base_dir/opt"
    package_usr_bin_dir="$package_base_dir/usr/bin"
}

purge_the_app() {
    print_info_message "Purging existing installation of ${app_name} (if installed)..."
    if dpkg -l | grep -q "^ii  ${app_name} "; then
        sudo apt purge --autoremove -y "${app_name}"
    else
        print_info_message "No existing installation found."
    fi
}

delete_the_old_files() {
    for dir in "${build_dirs[@]}"; do
        if [[ -d "$dir" ]]; then
            print_info_message "Removing existing directory: $dir"
            sudo rm -rf "$dir"
        fi
    done

    if [[ -f "$installer" ]]; then
        print_info_message "Removing existing installer: $installer"
        sudo rm -f "$installer"
    fi
}

create_a_new_executable_file() {
    print_info_message 'Creating the executable file...'
    pyinstaller $app_name.spec
}

package_the_tool() {
    # Create a directory hierarchy to package your application
    print_info_message "Creating package directory hierarchy..."
    mkdir -p $package_opt_dir
    mkdir -p $package_usr_bin_dir

    # Copy required files and folders into the package
    print_info_message "Copying the executable application into $package_opt_dir"
    sudo cp -r dist/netscout $package_opt_dir
    print_info_message "Creating a symbolink to $$package_usr_bin_dir/$app_name"
    ln -s /opt/netscout/netscout "$package_usr_bin_dir/$app_name"

    # Set the permissions and file ownerships
    print_info_message "Setting permissions and ownership for package directory..."
    sudo chmod 755 -R $package_base_dir
    sudo chown "${username}:${username}" -R $package_base_dir
}

create_installer() {
    print_info_message 'Creating the installer...'
    fpm -C "package" -s dir -t deb -n "${app_name}" -v "${version}" -p "${installer}" --after-install post_install_script.sh
}

start_the_installer() {
    print_info_message "Installing the new ${app_name} app."
    sudo dpkg -i "${installer}"
}

main