<?xml version="1.0" encoding="UTF-8"?>
<!--
Sépare la licence des conditions d'accès

https://ecospheres.gitbook.io/recommandations-iso-dcat/adaptation-des-metadonnees-iso-19139-pour-faciliter-la-transformation-en-dcat/separer-la-licence-des-conditions-dacces

Le snippet:

    <gmd:resourceConstraints>
      <gmd:MD_LegalConstraints>
        <gmd:accessConstraints>
          <gmd:MD_RestrictionCode codeList="http://standards.iso.org/iso/19139/resources/gmxCodelists.xml#MD_RestrictionCode"
                                  codeListValue="intellectualPropertyRights"/>
        </gmd:accessConstraints>
        <gmd:useConstraints>
          <gmd:MD_RestrictionCode codeList="http://standards.iso.org/iso/19139/resources/gmxCodelists.xml#MD_RestrictionCode"
                                  codeListValue="otherRestrictions"/>
        </gmd:useConstraints>
        <gmd:otherConstraints>
        <gco:CharacterString>
          The data is available under licence from Spatial Information Infrastructure
        </gco:CharacterString>
        </gmd:otherConstraints>
      </gmd:MD_LegalConstraints>
    </gmd:resourceConstraints>

Devient:

    <gmd:resourceConstraints>
      <gmd:MD_LegalConstraints>
        <gmd:accessConstraints>
          <gmd:MD_RestrictionCode codeList="http://standards.iso.org/iso/19139/resources/gmxCodelists.xml#MD_RestrictionCode"
                                  codeListValue="intellectualPropertyRights"/>
        </gmd:accessConstraints>
      </gmd:MD_LegalConstraints>
      <gmd:MD_LegalConstraints>
        <gmd:useConstraints>
          <gmd:MD_RestrictionCode codeList="http://standards.iso.org/iso/19139/resources/gmxCodelists.xml#MD_RestrictionCode"
                                  codeListValue="otherRestrictions"/>
        </gmd:useConstraints>
        <gmd:otherConstraints>
        <gco:CharacterString>
          The data is available under licence from Spatial Information Infrastructure
        </gco:CharacterString>
      </gmd:otherConstraints>
    </gmd:resourceConstraints>

NOTES:
- Ajout en cas d'absence ?
- Quid des cas codeListValue != 'otherRestrictions' ?
-->

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="2.0"
                xmlns:gmd="http://www.isotc211.org/2005/gmd"
                xmlns:geonet="http://www.fao.org/geonetwork"
                exclude-result-prefixes="#all">

  <xsl:template match="/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/
                       gmd:resourceConstraints[gmd:MD_LegalConstraints]"
                priority="2">
      <gmd:resourceConstraints>
        <xsl:for-each select="gmd:MD_LegalConstraints[gmd:accessConstraints]">
          <gmd:MD_LegalConstraints>
            <xsl:copy-of select="gmd:accessConstraints"/>
            <xsl:if test="gmd:accessConstraints/gmd:MD_RestrictionCode[@codeListValue='otherRestrictions']">
              <xsl:copy-of select="gmd:otherConstraints"/>
            </xsl:if>
          </gmd:MD_LegalConstraints>
        </xsl:for-each>
        <xsl:for-each select="gmd:MD_LegalConstraints[gmd:useConstraints]">
          <gmd:MD_LegalConstraints>
            <xsl:copy-of select="gmd:useConstraints"/>
            <xsl:if test="gmd:useConstraints/gmd:MD_RestrictionCode[@codeListValue='otherRestrictions']">
              <xsl:copy-of select="gmd:otherConstraints"/>
            </xsl:if>
          </gmd:MD_LegalConstraints>
        </xsl:for-each>
      </gmd:resourceConstraints>
  </xsl:template>

  <!--
      GUI integration
  -->

  <xsl:template name="list-ecospheres-split-constraints">
    <suggestion process="ecospheres-split-constraints"/>
  </xsl:template>

  <xsl:template name="analyze-ecospheres-split-constraints">
    <xsl:param name="root"/>
    <!-- TODO: conditional trigger -->
    <suggestion process="ecospheres-split-constraints" id="{generate-id()}">
      <name xml:lang="en">
        Apply ecospheres-split-constraints
      </name>
      <operational>true</operational>
      <form/>
    </suggestion>
  </xsl:template>

  <!--
      Geonetwork internals
  -->
  
  <!-- Do a copy of every nodes and attributes -->
  <xsl:template match="@*|node()">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
    </xsl:copy>
  </xsl:template>

  <!-- Remove geonet:* elements. -->
  <xsl:template match="geonet:*" priority="2"/>
</xsl:stylesheet>
