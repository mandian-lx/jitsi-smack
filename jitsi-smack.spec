%{?_javapackages_macros:%_javapackages_macros}

%define commit 2fa36c6a92821ebedc395da75c7a74e2d0cd6c89
%define shortcommit %(c=%{commit}; echo ${c:0:7})

%define tname Smack
%define oname %(echo %{tname} | tr [:upper:] [:lower:])

%define oversion 3_2_2
%define version %(echo %{oversion} | tr _ \. )

Summary:	An Open Source, cross-platform, easy to use Java XMPP client library
Name:		jitsi-%{oname}
Version:	%{version}
Release:	1
License:	ASL 2.0
Group:		Development/Java
URL:		https://github.com/jitsi/smack_%{oversion}
Source0:	https://github.com/jitsi/%{oname}_%{oversion}/archive/%{commit}/%{oname}_%{oversion}-%{commit}.zip
BuildArch:	noarch

BuildRequires:	maven-local
BuildRequires:	mvn(com.github.igniterealtime:jbosh)
BuildRequires:	mvn(com.jcraft:jzlib)
BuildRequires:	mvn(org.apache.felix:maven-bundle-plugin)
BuildRequires:	mvn(xpp3:xpp3)

%description
Smack is an Open Source [XMPP (Jabber)] client library for instant
messaging and presence. A pure Java library, it can be embedded into
your applications to create anything from a full XMPP client to simple
XMPP integrations such as sending notification messages and
presence-enabling devices.

NOTE: this is a Jisti fork of Smack library user by Jitsi client. You
don't need to manually install this package unsless you really know
what you aro doing.

%files -f .mfiles
%doc %{oname}/tags/%{oname}_%{oversion}/build/README.html

#----------------------------------------------------------------------------

%package javadoc
Summary:	Javadoc for %{tname}
BuildArch:	noarch

%description javadoc
API documentation for %{tname}.

%files javadoc -f .mfiles-javadoc

#----------------------------------------------------------------------------

%prep
%setup -q -n %{oname}_%{oversion}-%{commit}
# Remove all pre-build binaries
find . -type f -name "*.jar" -delete
find . -type f -name "*.class" -delete
find . -type f -name "*.dll" -delete

# Remove prebuilt documentation
rm -rf %{oname}/tags/%{oname}_%{oversion}/documentation/*

# Change project groupId to avoid mismatch
%pom_xpath_replace "pom:project/pom:groupId" \
	 "<groupId>org.jitsi</groupId>" \
	 %{oname}/tags/%{oname}_%{oversion}/build/m2/pom.xml

# Fix version
%pom_xpath_replace "pom:project/pom:version" "<version>%{version}</version>" %{oname}/tags/%{oname}_%{oversion}/build/m2/pom.xml

# Some fixes in modules
for m in %{oname} %{oname}x
do
	# fix missing version warnings
	%pom_xpath_inject "pom:plugin[pom:artifactId[./text()='maven-compiler-plugin']]" \
		"<version>any</version>" \
		%{oname}/tags/%{oname}_%{oversion}/build/m2/$m
	%pom_xpath_inject "pom:plugin[pom:artifactId[./text()='maven-jar-plugin']]" \
		"<version>any</version>" \
		%{oname}/tags/%{oname}_%{oversion}/build/m2/$m

	# change parent groupId according to project groupId
	%pom_xpath_replace "pom:parent/pom:groupId" \
		"<groupId>org.jitsi</groupId>" \
	 	%{oname}/tags/%{oname}_%{oversion}/build/m2/$m

        # fix parent version
        %pom_xpath_replace "pom:parent/pom:version" \
        	"<version>%{version}</version>" \
        	%{oname}/tags/%{oname}_%{oversion}/build/m2/$m

	# OSGify modules
	%pom_xpath_replace "pom:project/pom:packaging" "<packaging>bundle</packaging>" \
		%{oname}/tags/%{oname}_%{oversion}/build/m2/$m
	
	%pom_add_plugin org.apache.felix:maven-bundle-plugin %{oname}/tags/%{oname}_%{oversion}/build/m2/$m "
		<extensions>true</extensions>
		<configuration>
			<instructions>
				<Bundle-SymbolicName>\${project.groupId}.\${project.artifactId}</Bundle-SymbolicName>
				<Bundle-Name>\${project.artifactId}</Bundle-Name>
				<Bundle-Version>\${project.version}</Bundle-Version>
			</instructions>
		</configuration>
		<executions>
			<execution>
				<id>bundle-manifest</id>
				<phase>process-classes</phase>
				<goals>
					<goal>manifest</goal>
				</goals>
			</execution>
		</executions>"

	%pom_xpath_inject "pom:plugin[pom:artifactId[./text()='maven-jar-plugin']]/pom:configuration" "
	<archive>
		<manifestFile>\${project.build.outputDirectory}/META-INF/MANIFEST.MF</manifestFile>
		<addMavenDescriptor>false</addMavenDescriptor>
	</archive>" \
	%{oname}/tags/%{oname}_%{oversion}/build/m2/$m
done

# Include images in smackx-debug
%pom_xpath_inject "pom:resources/pom:resource/pom:includes" "
	<include>images/</include>" \
	%{oname}/tags/%{oname}_%{oversion}/build/m2/%{oname}x

# Include debugger in smackx (required by jitsi)
%pom_xpath_remove "pom:plugin[pom:artifactId[./text()='maven-compiler-plugin']]/pom:configuration/pom:excludes" \ 
	 %{oname}/tags/%{oname}_%{oversion}/build/m2/%{oname}x
%pom_xpath_remove "pom:plugin[pom:artifactId[./text()='maven-jar-plugin']]/pom:configuration/pom:excludes" \ 
	 %{oname}/tags/%{oname}_%{oversion}/build/m2/%{oname}x


# Remove classpath in manifest (fix class-path-in-manifest warning)
%pom_xpath_remove "pom:Class-Path" \
	 %{oname}/tags/%{oname}_%{oversion}/build/m2/%{oname}x

# Set the right name to fit the packaging guidelines
%mvn_file ":{*}" %{name}/@1-%{version} %{name}/@1

# Strip parent
%mvn_package :%{oname}-universe __noinstall

%build
%mvn_build -- -f %{oname}/tags/%{oname}_%{oversion}/build/m2

%install
%mvn_install -J %{oname}/tags/%{oname}_%{oversion}/build/m2/target/site/apidocs

