interfaces {
    restore-original-config-on-shutdown: false
    interface eth0 {
        description: "Internal pNodes interface"
        disable: false
        default-system-config
    }
}

protocols {
    igmp {
        disable: false
        interface eth0 {
            vif eth0 {
                disable: false
                version: 3
            }
        }
        traceoptions {
            flag all {
                disable: false
            }
        }
    }
}
