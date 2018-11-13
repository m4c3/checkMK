CHECK_ORACLE_HEALTH := check_oracle_health
CHECK_ORACLE_HEALTH_VERS := 3.0.1
CHECK_ORACLE_HEALTH_DIR = $(CHECK_ORACLE_HEALTH)-$(CHECK_ORACLE_HEALTH_VERS)

CHECK_ORACLE_HEALTH_BUILD := $(BUILD_HELPER_DIR)/$(CHECK_ORACLE_HEALTH_DIR)-build
CHECK_ORACLE_HEALTH_INSTALL := $(BUILD_HELPER_DIR)/$(CHECK_ORACLE_HEALTH_DIR)-install
CHECK_ORACLE_HEALTH_UNPACK := $(BUILD_HELPER_DIR)/$(CHECK_ORACLE_HEALTH_DIR)-unpack
CHECK_ORACLE_HEALTH_SKEL := $(BUILD_HELPER_DIR)/$(CHECK_ORACLE_HEALTH_DIR)-skel

.PHONY: $(CHECK_ORACLE_HEALTH) $(CHECK_ORACLE_HEALTH)-install $(CHECK_ORACLE_HEALTH)-skel $(CHECK_ORACLE_HEALTH)-clean

$(CHECK_ORACLE_HEALTH): $(CHECK_ORACLE_HEALTH_BUILD)

$(CHECK_ORACLE_HEALTH)-install: $(CHECK_ORACLE_HEALTH_INSTALL)

$(CHECK_ORACLE_HEALTH)-skel: $(CHECK_ORACLE_HEALTH_SKEL)

# Configure options for Nagios. Since we want to compile
# as non-root, we use our own user and group for compiling.
# All files will be packaged as user 'root' later anyway.
CHECK_ORACLE_HEALTH_CONFIGUREOPTS = ""

$(CHECK_ORACLE_HEALTH_BUILD): $(CHECK_ORACLE_HEALTH_UNPACK)
	for i in configure.ac aclocal.m4 configure Makefile.am Makefile.in ; do \
	  test -f $(CHECK_ORACLE_HEALTH_DIR)/$$i && touch $(CHECK_ORACLE_HEALTH_DIR)/$$i ; \
	done
	cd $(CHECK_ORACLE_HEALTH_DIR) ; ./configure $(CHECK_ORACLE_HEALTH_CONFIGUREOPTS)
	$(MAKE) -C $(CHECK_ORACLE_HEALTH_DIR)

$(CHECK_ORACLE_HEALTH_INSTALL): $(CHECK_ORACLE_HEALTH_BUILD)
	[ -d $(DESTDIR)$(OMD_ROOT)/lib/nagios/plugins ] || mkdir -p $(DESTDIR)$(OMD_ROOT)/lib/nagios/plugins
	install -m 755 $(CHECK_ORACLE_HEALTH_DIR)/plugins-scripts/check_oracle_health $(DESTDIR)$(OMD_ROOT)/lib/nagios/plugins

$(CHECK_ORACLE_HEALTH_SKEL):

$(CHECK_ORACLE_HEALTH)-clean:
	rm -rf $(CHECK_ORACLE_HEALTH_DIR) $(BUILD_HELPER_DIR)/$(CHECK_ORACLE_HEALTH_DIR)*
