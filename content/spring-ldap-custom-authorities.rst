Using custom authorities with spring-security LDAP authentication
#################################################################

:date: 2013-10-14 08:55
:tags: spring, spring-security, java, ldap, authentication
:category: spring
:slug: spring-ldap-custom-authorities
:author: Serafeim Papastefanos
:summary: Configuring spring-security for logging in through LDAP but retrieving the user's authorities from a custom (non-ldap) source.

.. contents::

Introduction
------------

One very useful component of the spring_ java framework is spring-security_ since it allows consistent usage of various security providers for
authentication and authorization. Although I've found a great number of basic spring-security tutorials on the internet, I wasn't able to find a complete solution for my own requirements:

Logging in with LDAP but configuring the authorities [*]_ of the logged in user with the help of a custom method and not through LDAP. 

I think that the above is a common requirement in many organizations: There is a central LDAP repository in which the usernames and passwords of the users are stored, but the groups of the users are not stored there. Or maybe the groups that are actually stored in the LDAP cannot be transformed easily to application specific groups for each application.

You may find the working spring project that uses ldap and a custom groups populator here: https://github.com/spapas/SpringLdapCustomAuthorities/

A basic spring security setup
-----------------------------

I've created a very basic setup for spring-security for a spring-mvc project. Please take a look here for a more thorough explanation of a simple spring-security project http://www.mkyong.com/spring-security/spring-security-hello-world-example/ and here http://www.codeproject.com/Articles/253901/Getting-Started-Spring-Security for a great explanation of the various spring-security classes.

In my setup there is a controller that defines two mappings, the "/" which is the homepage that has a link to the "/enter" and the "/enter" which is an internal page in which only authorized users have access. When the user clicks on "enter" he will be represented with a login form first. If the use logs in successfully, the enter.jsp will list the username and the authorities of the logged in user through the following spring-security tags:

.. code-block:: jsp


 <%@ taglib prefix="sec" uri="http://www.springframework.org/security/tags" %>
 [...]
 Username: <sec:authentication property="principal.username" /><br />
 Authorities: <sec:authentication property="principal.authorities"/><br />

The authentication provider is an in memory service in which the username, password and authorities of each user are defined in the XML. So this is a simple spring-security example that can be found in a number of places on the internet. The security rules, login form and the authentication provider are configured with the following ``security-config.xml``:

.. code-block:: xml

 <beans:beans xmlns="http://www.springframework.org/schema/security"
    xmlns:beans="http://www.springframework.org/schema/beans"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.springframework.org/schema/beans 
                    http://www.springframework.org/schema/beans/spring-beans-3.1.xsd
                    http://www.springframework.org/schema/security 
                    http://www.springframework.org/schema/security/spring-security-3.1.xsd">

    <http pattern="/static/**" security="none" />
    
    <http use-expressions="true">
        <intercept-url pattern="/" access="permitAll" />
        <intercept-url pattern="/enter" access="hasRole('user')" />
        <intercept-url pattern="/**" access="denyAll" />
        <form-login default-target-url="/" />
        <logout  logout-success-url="/" />    
    </http>

    <authentication-manager>
        <authentication-provider>
            <user-service>
                <user name="spapas" password="123" authorities="admin, user, nonldap" />
                <user name="serafeim" password="123" authorities="user" />
            </user-service>
        </authentication-provider>
    </authentication-manager>
    
 </beans:beans> 


When we run this application and go to the /enter, we will get the following output:

 Username: spapas

 Authorities: [admin, nonldap, user]

Spring security LDAP with custom authorities
--------------------------------------------

The previous application can be modified to login through LDAP and get the authorities from a custom class. The main differences are in the ``pom.xml`` which adsd the ``spring-security-ldap`` dependency, the addition of a ``CustomLdapAuthoritiesPopulator.java`` which does the actual mapping of username to authority and various changes to the ``security-config.xml``. 

As you will see we had to define our security beans mainly using spring beans and not using the various elements from security namespace like ``<ldap-server>`` and ``<ldap-authentication-provder>``. For a good tutorial on using these elements and ldap in spring security in general check these out: http://docs.spring.io/spring-security/site/docs/3.1.x/reference/ldap.html and http://krams915.blogspot.gr/2011/01/spring-security-mvc-using-ldap.html.

.. code-block:: xml

 <beans:beans xmlns="http://www.springframework.org/schema/security"
    xmlns:beans="http://www.springframework.org/schema/beans"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.springframework.org/schema/beans 
                    http://www.springframework.org/schema/beans/spring-beans-3.1.xsd
                    http://www.springframework.org/schema/security 
                    http://www.springframework.org/schema/security/spring-security-3.1.xsd">

    <http pattern="/static/**" security="none" />
    
    <http use-expressions="true" >
      <intercept-url pattern="/" access="permitAll" />
      <intercept-url pattern="/enter" access="hasRole('user')" />
      <intercept-url pattern="/**" access="denyAll" />
      <form-login default-target-url="/" />      
      <logout  logout-success-url="/" />    
    </http>
    
    <beans:bean id="contextSource" 
          class="org.springframework.security.ldap.DefaultSpringSecurityContextSource">
      <beans:constructor-arg value="ldap://login.serafeim.gr:389/dc=serafeim,dc=gr"/>
      <beans:property name="anonymousReadOnly" value="true"/> 		
    </beans:bean>
	
    <beans:bean 
          id="userSearch" 
          class="org.springframework.security.ldap.search.FilterBasedLdapUserSearch">
      <beans:constructor-arg index="0" value=""/>
      <beans:constructor-arg index="1" value="(uid={0})"/>
      <beans:constructor-arg index="2" ref="contextSource" />
    </beans:bean> 
    
    <beans:bean 
          id="ldapAuthProvider" 
          class="org.springframework.security.ldap.authentication.LdapAuthenticationProvider">
      <beans:constructor-arg>
        <beans:bean class="org.springframework.security.ldap.authentication.BindAuthenticator">
          <beans:constructor-arg ref="contextSource"/>
          <beans:property name="userSearch" ref="userSearch" />
          <!-- 
          <beans:property name="userDnPatterns">
            <beans:list><beans:value>uid={0},ou=People</beans:value></beans:list>
          </beans:property>
          -->
        </beans:bean>
      </beans:constructor-arg>
      <beans:constructor-arg>
        <beans:bean class="gr.serafeim.springldapcustom.CustomLdapAuthoritiesPopulator" />
      </beans:constructor-arg>
    </beans:bean>
	
    <authentication-manager>
      <authentication-provider ref="ldapAuthProvider" />
    </authentication-manager>

 </beans:beans> 


So, in the above configuration we've defined three spring beans: ``contextSource``, ``userSearch`` and ``ldapAuthProvider``. The ``<authentication-manager>`` element uses the ``ldapAuthProvider`` as an authentication provider. Below we will explain these beans:

contextSource
~~~~~~~~~~~~~

The contextSource bean defines the actual LDAP server that we are going to connect to. It has the class ``o.s.s.ldap.DefaultSpringSecurityContextSource``. This will need to be passed to other beans that would need to connect to the server for a number of operations. We pass to it the url of our LDAP server and set its ``anonymousReadOnly`` property to true. The ``anonymousReadOnly`` defines if we can anonymously connect to our LDAP server in order to perform the search operation below. If we cannot connect anonymously then we have to set its ``userDn`` and ``password`` properties.

A very interesting question is if the ``<ldap-server>`` element of the spring security namespace is related to ``the o.s.s.ldap.DefaultSpringSecurityContextSource`` like our ``contextSource``. To find out, we need to check the ``o.s.s.config.SecurityNamespaceHandler`` class of the ``spring-security-config.jar``. In there we see the ``loadParsers`` method which has the line: ``parsers.put(Elements.LDAP_SERVER, new LdapServerBeanDefinitionParser());``. The constant ``o.s.s.config.Elements.LDAP_SERVER`` has the value of ``"ldap-server"`` as expected, so we need to see what does the class ``o.s.s.config.ldap.LdapServerBeanDefinitionParser`` do. This class has a parse() method that receives the xml that was used to instantiate the ``<ldap-server>`` element and, depending an on the actualy configuration, instantiates a bean of the class ``o.s.s.ldap.DefaultSpringSecurityContextSource`` with an id of ``o.s.s.securityContextSource`` that will be used by the other elements in the security namespace !

This actually solves another question I had concerning the following error:

 No bean named 'org.springframework.security.authenticationManager' is defined: Did you forget to add a gobal <authentication-manager> element to your configuration (with child <authentication-provider>  elements)? Alternatively you can use the authentication-manager-ref attribute on your <http> and <global-method-security> elements.

What happens is that when spring-security-configuration encounters an ``<authentication-manager>`` it will instantiate a bean named ``o.s.s.authenticationManager``  having the class 
``o.s.s.authentication.ProviderManager`` and will create and pass to it a ``providers`` list with all the authentication providers that are defined inside the ``<authentication-manager>`` element with ``<authentication-provider>`` nodes. So, if you encounter the above error, the problem is that for some reason your ``<authentication-manager>`` is not configured correctly, so no ``o.s.s.authenticatioManager`` bean is created!

userSearch
~~~~~~~~~~

The ``userSearch`` bean is needed if we don't know exactly where our users are stored in the LDAP directory so we will use this bean as a search filter. If we do know our user tree then we won't need this bean at all as will be explained later. It has the class ``o.s.s.ldap.search.FilterBasedLdapUserSearch`` and gets three constructor parameters: ``searchBase``, ``searchFilter`` and ``contextSource``. The ``searchBase`` is from where in the LDAP tree to start searching (empty in our case), the ``searchFilter`` defines where is the username (uid in our case) and the ``contextSource`` has been defined before.

ldapAuthProvider
~~~~~~~~~~~~~~~~

This is the actual ``authentication-provider`` that the spring-security ``authentication-manager`` is going to use. It is an instance of class ``o.s.s.ldap.authentication.LdapAuthenticationProvider`` which has two main properties: An ``o.s.s.ldap.authentication.LdapAuthenticator`` implementation and an ``o.s.s.ldap.userdetails.LdapAuthoritiesPopulator`` implementation. The first interface defines an ``authenticate`` method and is used to actually authenticate the user with the LDAP server. The second interface defines a ``getGrantedAuthorities`` which returns the roles for the authenticated user. The LdapAuthoritiesPopulator parameter is actually optional (so we can use LDAP to authenticate only the users) and we can provide our own implementation to have custom authorities for our application. That is exactly what we've done here.

The two arguments used to initialize the ldapAuthProvoder are one instance of ``o.s.s.ldap.authentication.BindAuthenticator`` which is a simple authenticator that tries to bind with the given credentials to the LDAP server to check the credentials and one instance of a custom class named ``g.s.s.CustomLdapAuthoritiesPopulator`` which is the actual implementation of the custom roles provider. The ``BindAuthenticator`` gets the ``contextSource`` as a constructor parameter and its ``userSearch`` property is set with the ``userSearch`` bean defined previously. If we instead knew the actual place of the users, we could use the commented out ``userDnPatterns`` property which takes a list of possible places in the LDAP catalog which will be checked for the username.

CustomLdapAuthoritiesPopulator
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``CustomLdapAuthoritiesPopulator`` just needs to implement the ``LdapAuthoritiesPopulator`` interface. Here's our implmentation:

.. code-block:: java
 :linenos: none

 package gr.serafeim.springldapcustom;

 import java.util.Collection;
 import java.util.HashSet;
 import org.springframework.ldap.core.DirContextOperations;
 import org.springframework.security.core.GrantedAuthority;
 import org.springframework.security.core.authority.SimpleGrantedAuthority;
 import org.springframework.security.ldap.userdetails.LdapAuthoritiesPopulator;
 import org.springframework.stereotype.Component;

 @Component
 public class CustomLdapAuthoritiesPopulator implements LdapAuthoritiesPopulator {
	@Override
	public Collection<? extends GrantedAuthority> getGrantedAuthorities(
			DirContextOperations userData, String username) {
		Collection<GrantedAuthority> gas = new HashSet<GrantedAuthority>();
		if(username.equals("spapas")) {
			gas.add(new SimpleGrantedAuthority("admin"));
		}
		gas.add(new SimpleGrantedAuthority("user"));
		return gas;
	}
 }


The ``getGrantedAuthorities`` just checks the username and add another role if it is a specific one. Of course here we would autowire our user roles repository and query the database to get the roles of the user, however I'm not going to do that for the case of simplicity.

Example
~~~~~~~

When we run this application and go to the /enter, after logging in with our LDAP credentials as spapas, we will get the following output:

 Username: spapas

 Authorities: [admin, user]


Conclusion
----------

In the previous a complete example of configuring a custom authorities populator was represented. Using this configuration we can login through the LDAP server of our organization but use application specific roles for our logged-in users.

.. font-size: 0.5em;
   vertical-align: top;


.. [*] Which is how spring calls the groups/roles the user belongs to
.. _spring: http://spring.io/
.. _spring-security: http://projects.spring.io/spring-security/
